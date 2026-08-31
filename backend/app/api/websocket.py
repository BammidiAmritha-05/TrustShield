import asyncio
from datetime import datetime, timezone
import json
import logging
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status

from app.ai_adapter.claim import AIClaimVerificationAdapter, default_claim_adapter
from app.ai_adapter.conversation import AIConversationAdapter, default_conversation_adapter
from app.ai_adapter.protection import AIProtectionAdapter, default_protection_adapter
from app.ai_adapter.risk import AIRiskAdapter, default_risk_adapter
from app.ai_adapter.transcription import AITranscriptionAdapter, default_transcription_adapter
from app.ai_adapter.voice_authenticity import AIVoiceAuthenticityAdapter, default_voice_authenticity_adapter
from app.config import settings
from app.models import (
    AudioChunkTooLargeError,
    AudioDecodeFailedError,
    AudioDurationInvalidError,
    AudioDurationTooLongError,
    ClaimVerificationFailedError,
    ClaimVerificationUnavailableError,
    ConversationIntelligenceFailedError,
    ConversationIntelligenceUnavailableError,
    EmptyAudioChunkError,
    EmptyAudioError,
    ProtectionAgentFailedError,
    ProtectionAgentUnavailableError,
    RiskEngineFailedError,
    RiskEngineUnavailableError,
    SessionAudioLimitExceededError,
    SessionStatus,
    TranscriptionFailedError,
    TranscriptionUnavailableError,
    UnsupportedAudioFormatError,
    VoiceAuthenticityFailedError,
    VoiceAuthenticityUnavailableError,
)
from app.services.audio_buffer_service import AudioBufferService, default_audio_buffer_service
from app.services.audio_decoder_service import AudioDecoderService, default_audio_decoder_service
from app.services.evidence_store import default_evidence_store
from app.services.session_service import SessionService, default_session_service

logger = logging.getLogger("trustshield-backend.websocket")

router = APIRouter()


def make_ws_event(event_type: str, session_id: str, payload: dict) -> dict:
    """Helper to build standardized WebSocket server events."""
    return {
        "type": event_type,
        "version": 1,
        "session_id": session_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "payload": payload
    }


@router.websocket("/{session_id}/stream")
async def session_websocket_stream(
    websocket: WebSocket,
    session_id: str,
    session_service: SessionService = Depends(lambda: default_session_service),
    audio_buffer_service: AudioBufferService = Depends(lambda: default_audio_buffer_service),
    decoder_service: AudioDecoderService = Depends(lambda: default_audio_decoder_service),
    transcription_adapter: AITranscriptionAdapter = Depends(lambda: default_transcription_adapter),
    voice_authenticity_adapter: AIVoiceAuthenticityAdapter = Depends(lambda: default_voice_authenticity_adapter),
    conversation_adapter: AIConversationAdapter = Depends(lambda: default_conversation_adapter),
    risk_adapter: AIRiskAdapter = Depends(lambda: default_risk_adapter),
    protection_adapter: AIProtectionAdapter = Depends(lambda: default_protection_adapter),
    claim_adapter: AIClaimVerificationAdapter = Depends(lambda: default_claim_adapter)
):
    # 1. Pre-connection session validation
    try:
        session = session_service.get_session(session_id)
    except HTTPException:
        await websocket.close(code=4004, reason=f"Session '{session_id}' not found.")
        return

    if not session.consent:
        await websocket.close(code=4003, reason="Explicit user consent required.")
        return

    if session.status == SessionStatus.ENDED:
        await websocket.close(code=4003, reason=f"Session '{session_id}' is already ended.")
        return

    # 2. Activate session if status is 'created'
    session_service.activate_session(session_id)

    # 3. Accept WebSocket connection
    await websocket.accept()

    # 4. Emit SESSION_STARTED event
    await websocket.send_json(make_ws_event("SESSION_STARTED", session_id, {"status": "active"}))
    session_service.record_event_metadata(session_id, "SESSION_STARTED", {"status": "active"})

    # 5. Receive loop
    try:
        while True:
            message = await websocket.receive()

            if message.get("type") == "websocket.disconnect":
                logger.info(f"WebSocket client disconnected cleanly for session {session_id}")
                default_evidence_store.clear_session(session_id)
                break

            # Handle Text Messages
            if "text" in message and message["text"] is not None:
                text_data = message["text"]

                if len(text_data.encode("utf-8")) > settings.MAX_WS_MESSAGE_BYTES:
                    await websocket.send_json(make_ws_event("ERROR", session_id, {
                        "code": "OVERSIZED_PAYLOAD",
                        "message": f"Payload exceeds maximum allowed size of {settings.MAX_WS_MESSAGE_BYTES} bytes."
                    }))
                    continue

                try:
                    data = json.loads(text_data)
                except Exception:
                    await websocket.send_json(make_ws_event("ERROR", session_id, {
                        "code": "MALFORMED_JSON",
                        "message": "Invalid JSON payload."
                    }))
                    continue

                if not isinstance(data, dict):
                    await websocket.send_json(make_ws_event("ERROR", session_id, {
                        "code": "INVALID_MESSAGE",
                        "message": "WebSocket message must be a JSON object."
                    }))
                    continue

                action = data.get("action")
                if not action:
                    await websocket.send_json(make_ws_event("ERROR", session_id, {
                        "code": "INVALID_MESSAGE",
                        "message": "Missing 'action' field in message."
                    }))
                    continue

                if action == "send_text":
                    text_val = data.get("text")
                    if not isinstance(text_val, str) or not text_val.strip():
                        await websocket.send_json(make_ws_event("ERROR", session_id, {
                            "code": "INVALID_TEXT",
                            "message": "Field 'text' must be a non-empty string."
                        }))
                        continue

                    if len(text_val) > settings.MAX_WS_TEXT_LENGTH:
                        await websocket.send_json(make_ws_event("ERROR", session_id, {
                            "code": "OVERSIZED_PAYLOAD",
                            "message": f"Text length exceeds maximum allowed length of {settings.MAX_WS_TEXT_LENGTH} characters."
                        }))
                        continue

                    await websocket.send_json(make_ws_event("TEXT_RECEIVED", session_id, {"text": text_val}))
                    session_service.record_event_metadata(session_id, "TEXT_RECEIVED", {"text_length": len(text_val)})

                    # 1. Run Conversation Intelligence
                    conv_res = None
                    try:
                        conv_res = await asyncio.to_thread(conversation_adapter.analyze_text, text_val)
                        await websocket.send_json(make_ws_event("SIGNAL_UPDATE", session_id, conv_res))
                        session_service.record_event_metadata(session_id, "SIGNAL_UPDATE", conv_res)
                    except ConversationIntelligenceUnavailableError as e:
                        await websocket.send_json(make_ws_event("SIGNAL_UPDATE", session_id, {
                            "status": "unavailable",
                            "reason": "module_unavailable",
                            "message": str(e)
                        }))
                    except ConversationIntelligenceFailedError as e:
                        await websocket.send_json(make_ws_event("SIGNAL_UPDATE", session_id, {
                            "status": "error",
                            "reason": "analysis_failed",
                            "message": str(e)
                        }))
                    except Exception as e:
                        logger.error(f"Unexpected error in conversation pipeline for text session {session_id}: {e}", exc_info=True)

                    # 2. Run Risk Engine Evaluation
                    risk_res = None
                    try:
                        risk_res = await asyncio.to_thread(
                            risk_adapter.evaluate_session_turn,
                            session_id,
                            conversation_analysis=conv_res
                        )
                        await websocket.send_json(make_ws_event("RISK_UPDATE", session_id, risk_res))
                        session_service.record_event_metadata(session_id, "RISK_UPDATE", risk_res)
                    except RiskEngineUnavailableError as e:
                        await websocket.send_json(make_ws_event("RISK_UPDATE", session_id, {
                            "status": "unavailable",
                            "reason": "risk_engine_unavailable",
                            "message": str(e)
                        }))
                    except RiskEngineFailedError as e:
                        await websocket.send_json(make_ws_event("RISK_UPDATE", session_id, {
                            "status": "error",
                            "reason": "risk_evaluation_failed",
                            "message": str(e)
                        }))
                    except Exception as e:
                        logger.error(f"Unexpected error in Risk Engine for text session {session_id}: {e}", exc_info=True)

                    # 3. Run Claim Verification Pipeline
                    try:
                        claim_res = await asyncio.to_thread(
                            claim_adapter.verify_claim,
                            text_val
                        )
                        await websocket.send_json(make_ws_event("CLAIM_VERIFICATION", session_id, claim_res))
                        session_service.record_event_metadata(session_id, "CLAIM_VERIFICATION", claim_res)
                    except ClaimVerificationUnavailableError as e:
                        await websocket.send_json(make_ws_event("CLAIM_VERIFICATION", session_id, {
                            "status": "unavailable",
                            "reason": "claim_verification_unavailable",
                            "message": str(e)
                        }))
                    except ClaimVerificationFailedError as e:
                        await websocket.send_json(make_ws_event("CLAIM_VERIFICATION", session_id, {
                            "status": "error",
                            "reason": "claim_verification_failed",
                            "message": str(e)
                        }))
                    except Exception as e:
                        logger.error(f"Unexpected error in Claim Verification for text session {session_id}: {e}", exc_info=True)

                    # 4. Run Protection Agent Guidance
                    if risk_res and risk_res.get("status") == "available":
                        try:
                            prot_res = await asyncio.to_thread(
                                protection_adapter.generate_guidance,
                                risk_res,
                                conversation_analysis=conv_res
                            )
                            await websocket.send_json(make_ws_event("PROTECTION_UPDATE", session_id, prot_res))
                            session_service.record_event_metadata(session_id, "PROTECTION_UPDATE", prot_res)
                        except ProtectionAgentUnavailableError as e:
                            await websocket.send_json(make_ws_event("PROTECTION_UPDATE", session_id, {
                                "status": "unavailable",
                                "reason": "protection_agent_unavailable",
                                "message": str(e)
                            }))
                        except ProtectionAgentFailedError as e:
                            await websocket.send_json(make_ws_event("PROTECTION_UPDATE", session_id, {
                                "status": "error",
                                "reason": "protection_guidance_failed",
                                "message": str(e)
                            }))
                        except Exception as e:
                            logger.error(f"Unexpected error in Protection Agent for text session {session_id}: {e}", exc_info=True)

                elif action == "flush_utterance":
                    # Finalize current spoken utterance
                    full_buffer_bytes = audio_buffer_service.get_buffer(session_id)
                    audio_buffer_service.clear_buffer(session_id)
                    if full_buffer_bytes:
                        try:
                            decoded = decoder_service.decode_audio(full_buffer_bytes)
                            if decoded and decoded.pcm_data:
                                transcribe_res = await asyncio.to_thread(
                                    transcription_adapter.transcribe_pcm_bytes,
                                    decoded.pcm_data,
                                    decoded.sample_rate
                                )
                                text = transcribe_res.get("text", "").strip()
                                conv_res = None
                                if text:
                                    final_payload = {
                                        "text": text,
                                        "duration": transcribe_res.get("duration", 0.0),
                                        "language": transcribe_res.get("language", "en")
                                    }
                                    await websocket.send_json(make_ws_event("TRANSCRIPT_FINAL", session_id, final_payload))
                                    session_service.record_event_metadata(session_id, "TRANSCRIPT_FINAL", final_payload)

                                    conv_res = await asyncio.to_thread(
                                        conversation_adapter.analyze_text,
                                        text
                                    )
                                    await websocket.send_json(make_ws_event("SIGNAL_UPDATE", session_id, conv_res))
                                    session_service.record_event_metadata(session_id, "SIGNAL_UPDATE", conv_res)

                                voice_res = await asyncio.to_thread(
                                    voice_authenticity_adapter.analyze_pcm_bytes,
                                    decoded.pcm_data,
                                    decoded.sample_rate
                                )

                                # Advance turn index for completed spoken utterance
                                risk_res = await asyncio.to_thread(
                                    risk_adapter.evaluate_session_turn,
                                    session_id,
                                    conversation_analysis=conv_res,
                                    voice_analysis=voice_res,
                                    advance_turn=True
                                )
                                await websocket.send_json(make_ws_event("RISK_UPDATE", session_id, risk_res))
                                session_service.record_event_metadata(session_id, "RISK_UPDATE", risk_res)

                                if text:
                                    claim_res = await asyncio.to_thread(
                                        claim_adapter.verify_claim,
                                        text
                                    )
                                    await websocket.send_json(make_ws_event("CLAIM_VERIFICATION", session_id, claim_res))
                                    session_service.record_event_metadata(session_id, "CLAIM_VERIFICATION", claim_res)

                                if risk_res and risk_res.get("status") == "available":
                                    prot_res = await asyncio.to_thread(
                                        protection_adapter.generate_guidance,
                                        risk_res,
                                        conversation_analysis=conv_res
                                    )
                                    await websocket.send_json(make_ws_event("PROTECTION_UPDATE", session_id, prot_res))
                                    session_service.record_event_metadata(session_id, "PROTECTION_UPDATE", prot_res)
                        except Exception as e:
                            logger.error(f"Error finalizing utterance for session {session_id}: {e}", exc_info=True)

                elif action == "stop":
                    session_service.end_session(session_id)
                    default_evidence_store.clear_session(session_id)
                    audio_buffer_service.clear_buffer(session_id)
                    ended_timestamp = datetime.now(timezone.utc).isoformat()
                    await websocket.send_json(make_ws_event("SESSION_ENDED", session_id, {
                        "status": "ended",
                        "ended_at": ended_timestamp
                    }))
                    session_service.record_event_metadata(session_id, "SESSION_ENDED", {"status": "ended"})
                    await websocket.close(code=1000, reason="Session ended by client stop command.")
                    break

                else:
                    await websocket.send_json(make_ws_event("ERROR", session_id, {
                        "code": "UNSUPPORTED_ACTION",
                        "message": f"Unsupported action '{action}'."
                    }))
                    continue

            # Handle Binary Audio Chunks
            elif "bytes" in message and message["bytes"] is not None:
                bytes_data = message["bytes"]

                # 5.1 Append to Audio Buffer
                try:
                    buffer_info = audio_buffer_service.append_chunk(session_id, bytes_data)
                    await websocket.send_json(make_ws_event("AUDIO_BUFFERED", session_id, buffer_info))
                    session_service.record_event_metadata(session_id, "AUDIO_BUFFERED", buffer_info)
                except EmptyAudioChunkError:
                    await websocket.send_json(make_ws_event("ERROR", session_id, {
                        "code": "EMPTY_AUDIO_CHUNK",
                        "message": "Binary audio chunk cannot be empty."
                    }))
                    continue
                except AudioChunkTooLargeError as e:
                    await websocket.send_json(make_ws_event("ERROR", session_id, {
                        "code": "AUDIO_CHUNK_TOO_LARGE",
                        "message": str(e)
                    }))
                    continue
                except SessionAudioLimitExceededError as e:
                    await websocket.send_json(make_ws_event("ERROR", session_id, {
                        "code": "SESSION_AUDIO_LIMIT_EXCEEDED",
                        "message": str(e)
                    }))
                    continue

                # 5.2 Attempt Decoding Buffered Audio
                full_buffer_bytes = audio_buffer_service.get_buffer(session_id)
                decoded = None
                try:
                    decoded = decoder_service.decode_audio(full_buffer_bytes)
                    metadata_payload = decoded.to_metadata_payload()
                    await websocket.send_json(make_ws_event("AUDIO_DECODED", session_id, metadata_payload))
                    session_service.record_event_metadata(session_id, "AUDIO_DECODED", metadata_payload)
                except UnsupportedAudioFormatError as e:
                    await websocket.send_json(make_ws_event("ERROR", session_id, {
                        "code": "UNSUPPORTED_AUDIO_FORMAT",
                        "message": str(e)
                    }))
                    continue
                except AudioDecodeFailedError as e:
                    await websocket.send_json(make_ws_event("ERROR", session_id, {
                        "code": "AUDIO_DECODE_FAILED",
                        "message": str(e)
                    }))
                    continue
                except AudioDurationTooLongError as e:
                    await websocket.send_json(make_ws_event("ERROR", session_id, {
                        "code": "AUDIO_DURATION_TOO_LONG",
                        "message": str(e)
                    }))
                    continue
                except AudioDurationInvalidError as e:
                    await websocket.send_json(make_ws_event("ERROR", session_id, {
                        "code": "AUDIO_DURATION_INVALID",
                        "message": str(e)
                    }))
                    continue
                except EmptyAudioError as e:
                    await websocket.send_json(make_ws_event("ERROR", session_id, {
                        "code": "EMPTY_AUDIO",
                        "message": str(e)
                    }))
                    continue

                # 5.3 Independent AI Execution & Multi-Modal Protection Pipeline
                if decoded and decoded.pcm_data:
                    final_transcript_text = ""
                    conv_res = None
                    voice_res = None
                    risk_res = None

                    # 5.3.1 Whisper Transcription Pipeline
                    try:
                        transcribe_res = await asyncio.to_thread(
                            transcription_adapter.transcribe_pcm_bytes,
                            decoded.pcm_data,
                            decoded.sample_rate
                        )

                        final_transcript_text = transcribe_res.get("text", "")
                        if final_transcript_text and final_transcript_text.strip():
                            partial_payload = {
                                "text": final_transcript_text,
                                "duration": transcribe_res.get("duration", 0.0),
                                "language": transcribe_res.get("language", "en")
                            }
                            await websocket.send_json(make_ws_event("TRANSCRIPT_PARTIAL", session_id, partial_payload))
                            session_service.record_event_metadata(session_id, "TRANSCRIPT_PARTIAL", partial_payload)

                    except TranscriptionUnavailableError as e:
                        await websocket.send_json(make_ws_event("ERROR", session_id, {
                            "code": "TRANSCRIPTION_UNAVAILABLE",
                            "message": str(e)
                        }))
                    except TranscriptionFailedError as e:
                        await websocket.send_json(make_ws_event("ERROR", session_id, {
                            "code": "TRANSCRIPTION_FAILED",
                            "message": str(e)
                        }))
                    except Exception as e:
                        logger.error(f"Unexpected error in Whisper pipeline for session {session_id}: {e}", exc_info=True)

                    # 5.3.2 AASIST Voice Authenticity Pipeline
                    try:
                        voice_res = await asyncio.to_thread(
                            voice_authenticity_adapter.analyze_pcm_bytes,
                            decoded.pcm_data,
                            decoded.sample_rate
                        )
                        await websocket.send_json(make_ws_event("VOICE_ANALYSIS", session_id, voice_res))
                        session_service.record_event_metadata(session_id, "VOICE_ANALYSIS", voice_res)

                    except VoiceAuthenticityUnavailableError as e:
                        await websocket.send_json(make_ws_event("VOICE_ANALYSIS", session_id, {
                            "status": "unavailable",
                            "reason": "model_unavailable",
                            "message": str(e)
                        }))
                    except VoiceAuthenticityFailedError as e:
                        await websocket.send_json(make_ws_event("VOICE_ANALYSIS", session_id, {
                            "status": "error",
                            "reason": "inference_failed",
                            "message": str(e)
                        }))
                    except Exception as e:
                        logger.error(f"Unexpected error in AASIST pipeline for session {session_id}: {e}", exc_info=True)

                    # 5.3.3 Conversation Intelligence Pipeline
                    if final_transcript_text and final_transcript_text.strip():
                        try:
                            conv_res = await asyncio.to_thread(
                                conversation_adapter.analyze_text,
                                final_transcript_text
                            )
                            await websocket.send_json(make_ws_event("SIGNAL_UPDATE", session_id, conv_res))
                            session_service.record_event_metadata(session_id, "SIGNAL_UPDATE", conv_res)
                        except ConversationIntelligenceUnavailableError as e:
                            await websocket.send_json(make_ws_event("SIGNAL_UPDATE", session_id, {
                                "status": "unavailable",
                                "reason": "module_unavailable",
                                "message": str(e)
                            }))
                        except ConversationIntelligenceFailedError as e:
                            await websocket.send_json(make_ws_event("SIGNAL_UPDATE", session_id, {
                                "status": "error",
                                "reason": "analysis_failed",
                                "message": str(e)
                            }))
                        except Exception as e:
                            logger.error(f"Unexpected error in Conversation Intelligence pipeline for session {session_id}: {e}", exc_info=True)

                    # 5.3.4 Multi-Modal Hybrid Risk Engine Pipeline (In-Flight Preview without advancing Turn)
                    try:
                        risk_res = await asyncio.to_thread(
                            risk_adapter.evaluate_session_turn,
                            session_id,
                            conversation_analysis=conv_res,
                            voice_analysis=voice_res,
                            advance_turn=False
                        )
                        await websocket.send_json(make_ws_event("RISK_UPDATE", session_id, risk_res))
                        session_service.record_event_metadata(session_id, "RISK_UPDATE", risk_res)
                    except RiskEngineUnavailableError as e:
                        await websocket.send_json(make_ws_event("RISK_UPDATE", session_id, {
                            "status": "unavailable",
                            "reason": "risk_engine_unavailable",
                            "message": str(e)
                        }))
                    except RiskEngineFailedError as e:
                        await websocket.send_json(make_ws_event("RISK_UPDATE", session_id, {
                            "status": "error",
                            "reason": "risk_evaluation_failed",
                            "message": str(e)
                        }))
                    except Exception as e:
                        logger.error(f"Unexpected error in Risk Engine pipeline for session {session_id}: {e}", exc_info=True)

                    # 5.3.5 Official Claim Verification Pipeline
                    if final_transcript_text and final_transcript_text.strip():
                        try:
                            claim_res = await asyncio.to_thread(
                                claim_adapter.verify_claim,
                                final_transcript_text
                            )
                            await websocket.send_json(make_ws_event("CLAIM_VERIFICATION", session_id, claim_res))
                            session_service.record_event_metadata(session_id, "CLAIM_VERIFICATION", claim_res)
                        except ClaimVerificationUnavailableError as e:
                            await websocket.send_json(make_ws_event("CLAIM_VERIFICATION", session_id, {
                                "status": "unavailable",
                                "reason": "claim_verification_unavailable",
                                "message": str(e)
                            }))
                        except ClaimVerificationFailedError as e:
                            await websocket.send_json(make_ws_event("CLAIM_VERIFICATION", session_id, {
                                "status": "error",
                                "reason": "claim_verification_failed",
                                "message": str(e)
                            }))
                        except Exception as e:
                            logger.error(f"Unexpected error in Claim Verification for voice session {session_id}: {e}", exc_info=True)

                    # 5.3.6 Protection Agent Guidance Pipeline
                    if risk_res and risk_res.get("status") == "available":
                        try:
                            prot_res = await asyncio.to_thread(
                                protection_adapter.generate_guidance,
                                risk_res,
                                conversation_analysis=conv_res
                            )
                            await websocket.send_json(make_ws_event("PROTECTION_UPDATE", session_id, prot_res))
                            session_service.record_event_metadata(session_id, "PROTECTION_UPDATE", prot_res)
                        except ProtectionAgentUnavailableError as e:
                            await websocket.send_json(make_ws_event("PROTECTION_UPDATE", session_id, {
                                "status": "unavailable",
                                "reason": "protection_agent_unavailable",
                                "message": str(e)
                            }))
                        except ProtectionAgentFailedError as e:
                            await websocket.send_json(make_ws_event("PROTECTION_UPDATE", session_id, {
                                "status": "error",
                                "reason": "protection_guidance_failed",
                                "message": str(e)
                            }))
                        except Exception as e:
                            logger.error(f"Unexpected error in Protection Agent pipeline for session {session_id}: {e}", exc_info=True)

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected cleanly for session {session_id}")
        default_evidence_store.clear_session(session_id)
    except Exception as e:
        logger.error(f"Unexpected error in WebSocket loop for session {session_id}: {e}", exc_info=True)
        try:
            await websocket.send_json(make_ws_event("ERROR", session_id, {
                "code": "SERVER_ERROR",
                "message": "An unexpected WebSocket error occurred."
            }))
        except Exception:
            pass
