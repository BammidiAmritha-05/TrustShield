import io
import logging
import wave
from typing import Dict, Tuple
import numpy as np
import scipy.signal as signal
import soundfile as sf

from app.config import settings
from app.models import (
    AudioDecodeFailedError,
    AudioDurationInvalidError,
    AudioDurationTooLongError,
    DecodedAudio,
    EmptyAudioError,
    UnsupportedAudioFormatError,
)

logger = logging.getLogger("trustshield-backend.audio_decoder")


class AudioDecoderService:
    """
    Decodes browser-compatible audio payloads into a normalized internal PCM representation
    (16 kHz, Mono, 16-bit signed PCM) matching TrustShield AI pipeline expectations.
    """

    def __init__(
        self,
        target_sample_rate: int = settings.TARGET_SAMPLE_RATE,
        target_channels: int = settings.TARGET_CHANNELS,
        target_sample_width: int = settings.TARGET_SAMPLE_WIDTH,
        max_duration_seconds: float = settings.MAX_AUDIO_DURATION_SECONDS,
    ):
        self.target_sample_rate = target_sample_rate
        self.target_channels = target_channels
        self.target_sample_width = target_sample_width
        self.max_duration_seconds = max_duration_seconds

    def detect_format(self, data: bytes) -> str:
        """Detects container format by header magic bytes."""
        if not data or len(data) == 0:
            return "empty"
        if data.startswith(b"RIFF") and b"WAVE" in data[:16]:
            return "wav"
        if data.startswith(b"OggS"):
            return "ogg"
        if data.startswith(b"fLaC"):
            return "flac"
        if data.startswith(b"FORM") and b"AIFF" in data[:12]:
            return "aiff"
        if data.startswith(b"\x1a\x45\xdf\xa3"):
            return "webm"
        return "unknown"

    def _decode_raw_bytes(self, data: bytes) -> Tuple[np.ndarray, int, str]:
        """Attempt decoding bytes via soundfile or wave standard library."""
        # 1. Try soundfile
        try:
            buf = io.BytesIO(data)
            audio_np, sr = sf.read(buf, dtype="int16")
            fmt = self.detect_format(data)
            return audio_np, sr, fmt if fmt != "unknown" else "wav"
        except Exception as sf_err:
            logger.debug(f"Soundfile decode attempt failed: {sf_err}")

        # 2. Try standard library wave module for uncompressed WAV (with multi-chunk concatenation support)
        try:
            # Check if multiple WAV chunks are concatenated in the buffer
            if data.startswith(b"RIFF"):
                riff_offsets = []
                idx = 0
                while True:
                    found = data.find(b"RIFF", idx)
                    if found == -1:
                        break
                    riff_offsets.append(found)
                    idx = found + 4

                if len(riff_offsets) > 1:
                    chunks_np = []
                    sr = 16000
                    for i, start_pos in enumerate(riff_offsets):
                        end_pos = riff_offsets[i + 1] if i + 1 < len(riff_offsets) else len(data)
                        chunk_bytes = data[start_pos:end_pos]
                        try:
                            c_buf = io.BytesIO(chunk_bytes)
                            with wave.open(c_buf, "rb") as wf:
                                sr = wf.getframerate()
                                nc = wf.getnchannels()
                                sw = wf.getsampwidth()
                                fr = wf.readframes(wf.getnframes())
                                if sw == 2:
                                    c_np = np.frombuffer(fr, dtype=np.int16)
                                elif sw == 1:
                                    c_np = (np.frombuffer(fr, dtype=np.uint8).astype(np.int16) - 128) * 256
                                elif sw == 4:
                                    c_np = (np.frombuffer(fr, dtype=np.int32) >> 16).astype(np.int16)
                                else:
                                    continue
                                if nc > 1:
                                    c_np = c_np.reshape(-1, nc)
                                chunks_np.append(c_np)
                        except Exception:
                            continue

                    if chunks_np:
                        audio_np = np.concatenate(chunks_np, axis=0)
                        return audio_np, sr, "wav"

            buf = io.BytesIO(data)
            with wave.open(buf, "rb") as wave_file:
                sr = wave_file.getframerate()
                nchannels = wave_file.getnchannels()
                sampwidth = wave_file.getsampwidth()
                frames = wave_file.readframes(wave_file.getnframes())

                if sampwidth == 2:
                    audio_np = np.frombuffer(frames, dtype=np.int16)
                elif sampwidth == 1:
                    audio_np = (np.frombuffer(frames, dtype=np.uint8).astype(np.int16) - 128) * 256
                elif sampwidth == 4:
                    audio_np = (np.frombuffer(frames, dtype=np.int32) >> 16).astype(np.int16)
                else:
                    raise AudioDecodeFailedError(f"Unsupported WAV sample width: {sampwidth} bytes.")

                if nchannels > 1:
                    audio_np = audio_np.reshape(-1, nchannels)

                return audio_np, sr, "wav"
        except wave.Error as wave_err:
            logger.debug(f"Wave module decode attempt failed: {wave_err}")

        # 3. Check container types
        fmt = self.detect_format(data)
        if fmt == "webm":
            raise UnsupportedAudioFormatError(
                f"Audio format '{fmt}' is unsupported or container header is incomplete."
            )

        raise AudioDecodeFailedError("Failed to decode audio payload: malformed audio container or unrecognized data.")

    def decode_audio(self, data: bytes) -> DecodedAudio:
        """
        Decodes raw audio bytes and normalizes output to 16 kHz Mono 16-bit PCM.
        """
        if not data or len(data) == 0:
            raise EmptyAudioError("Input audio payload for decoding is empty.")

        audio_np, orig_sr, detected_fmt = self._decode_raw_bytes(data)

        if audio_np is None or len(audio_np) == 0:
            raise AudioDurationInvalidError("Decoded audio sample count is zero.")

        # 1. Normalize channels to Mono
        if audio_np.ndim > 1 and audio_np.shape[1] > 1:
            # Average multi-channel array across axis 1
            audio_mono = audio_np.mean(axis=1).astype(np.float32)
        else:
            audio_mono = audio_np.squeeze().astype(np.float32)

        # 2. Normalize sample rate to 16 kHz
        if orig_sr != self.target_sample_rate:
            if orig_sr <= 0:
                raise AudioDurationInvalidError(f"Invalid original sample rate: {orig_sr} Hz.")
            target_num_samples = int(round(len(audio_mono) * (self.target_sample_rate / orig_sr)))
            if target_num_samples <= 0:
                raise AudioDurationInvalidError("Resampled sample count is zero.")
            
            resampled = signal.resample(audio_mono, target_num_samples)
            final_pcm_np = np.clip(resampled, -32768, 32767).astype(np.int16)
        else:
            final_pcm_np = np.clip(audio_mono, -32768, 32767).astype(np.int16)

        sample_count = len(final_pcm_np)
        if sample_count == 0:
            raise AudioDurationInvalidError("Decoded audio sample count is zero.")

        duration_seconds = sample_count / float(self.target_sample_rate)

        if duration_seconds <= 0:
            raise AudioDurationInvalidError("Decoded audio duration must be greater than zero.")

        if duration_seconds > self.max_duration_seconds:
            raise AudioDurationTooLongError(
                f"Audio duration ({duration_seconds:.2f}s) exceeds maximum allowed limit of {self.max_duration_seconds:.2f}s."
            )

        return DecodedAudio(
            sample_rate=self.target_sample_rate,
            channels=self.target_channels,
            sample_width=self.target_sample_width,
            sample_count=sample_count,
            duration_seconds=duration_seconds,
            format="pcm_s16le",
            codec="pcm_s16le",
            pcm_data=final_pcm_np.tobytes()
        )


# Global audio decoder service instance
default_audio_decoder_service = AudioDecoderService()
