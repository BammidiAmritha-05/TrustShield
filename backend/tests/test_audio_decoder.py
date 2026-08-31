import io
import os
import wave
import numpy as np
import pytest
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
from app.services.audio_decoder_service import AudioDecoderService


def make_synthetic_wav_bytes(
    sample_rate: int = 16000,
    channels: int = 1,
    duration_seconds: float = 1.0,
    frequency: float = 440.0
) -> bytes:
    """Generates synthetic PCM WAV audio bytes strictly in memory."""
    num_samples = int(sample_rate * duration_seconds)
    t = np.linspace(0, duration_seconds, num_samples, endpoint=False)
    # Sine wave scaled to int16
    mono_signal = (np.sin(2 * np.pi * frequency * t) * 16384).astype(np.int16)

    if channels == 2:
        signal_data = np.column_stack((mono_signal, mono_signal))
    else:
        signal_data = mono_signal

    buf = io.BytesIO()
    sf.write(buf, signal_data, sample_rate, format="WAV", subtype="PCM_16")
    return buf.getvalue()


def test_valid_wav_decode():
    """1. Decode valid WAV bytes."""
    service = AudioDecoderService()
    wav_bytes = make_synthetic_wav_bytes(sample_rate=16000, channels=1, duration_seconds=1.5)
    decoded = service.decode_audio(wav_bytes)

    assert isinstance(decoded, DecodedAudio)
    assert decoded.sample_rate == 16000
    assert decoded.channels == 1
    assert decoded.sample_width == 2
    assert decoded.sample_count == 24000
    assert pytest.approx(decoded.duration_seconds, 0.01) == 1.5
    assert decoded.format == "pcm_s16le"


def test_mono_audio_preservation():
    """2. Preserve mono channel count."""
    service = AudioDecoderService()
    wav_bytes = make_synthetic_wav_bytes(sample_rate=16000, channels=1, duration_seconds=1.0)
    decoded = service.decode_audio(wav_bytes)
    assert decoded.channels == 1


def test_stereo_to_mono_normalization():
    """3. Normalize stereo WAV audio to mono."""
    service = AudioDecoderService()
    stereo_bytes = make_synthetic_wav_bytes(sample_rate=16000, channels=2, duration_seconds=1.0)
    decoded = service.decode_audio(stereo_bytes)
    assert decoded.channels == 1
    assert decoded.sample_count == 16000


def test_sample_rate_normalization_to_16k():
    """4. Resample 44.1 kHz audio to 16 kHz."""
    service = AudioDecoderService()
    high_sr_bytes = make_synthetic_wav_bytes(sample_rate=44100, channels=1, duration_seconds=1.0)
    decoded = service.decode_audio(high_sr_bytes)

    assert decoded.sample_rate == 16000
    assert decoded.sample_count == 16000
    assert pytest.approx(decoded.duration_seconds, 0.01) == 1.0


def test_empty_input_rejection():
    """5. Empty byte payload raises EmptyAudioError."""
    service = AudioDecoderService()
    with pytest.raises(EmptyAudioError):
        service.decode_audio(b"")


def test_malformed_input_rejection():
    """6. Malformed garbage bytes raise AudioDecodeFailedError."""
    service = AudioDecoderService()
    malformed_bytes = b"RIFF_FAKE_HEADER_GARBAGE_BYTES_1234567890"
    with pytest.raises(AudioDecodeFailedError):
        service.decode_audio(malformed_bytes)


def test_unsupported_format_rejection():
    """7. Unsupported WebM header bytes raise UnsupportedAudioFormatError."""
    service = AudioDecoderService()
    webm_header_bytes = b"\x1a\x45\xdf\xa3\x99\x88\x77\x66\x55\x44"
    with pytest.raises(UnsupportedAudioFormatError):
        service.decode_audio(webm_header_bytes)


def test_invalid_duration_rejection():
    """8. Zero length decoded signal raises AudioDurationInvalidError."""
    service = AudioDecoderService()
    # Create empty WAV with 0 frames
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        wf.writeframes(b"")
    zero_wav = buf.getvalue()

    with pytest.raises(AudioDurationInvalidError):
        service.decode_audio(zero_wav)


def test_maximum_duration_exceeded():
    """9. Audio duration exceeding max limit raises AudioDurationTooLongError."""
    service = AudioDecoderService(max_duration_seconds=2.0)
    long_wav = make_synthetic_wav_bytes(sample_rate=16000, channels=1, duration_seconds=3.0)

    with pytest.raises(AudioDurationTooLongError):
        service.decode_audio(long_wav)


def test_decoded_metadata_correctness():
    """10. Metadata payload dictionary formatting."""
    service = AudioDecoderService()
    wav_bytes = make_synthetic_wav_bytes(sample_rate=16000, channels=1, duration_seconds=1.25)
    decoded = service.decode_audio(wav_bytes)

    meta = decoded.to_metadata_payload()
    assert meta == {
        "sample_rate": 16000,
        "channels": 1,
        "sample_width": 2,
        "sample_count": 20000,
        "duration_seconds": 1.25,
        "format": "pcm_s16le",
        "codec": "pcm_s16le"
    }


def test_zero_disk_file_persistence():
    """11. Verify raw decoded audio is not written to permanent files on disk."""
    service = AudioDecoderService()
    test_wav = make_synthetic_wav_bytes(sample_rate=16000, channels=1, duration_seconds=1.0)
    decoded = service.decode_audio(test_wav)

    target_bytes = decoded.pcm_data[:32]

    disk_found = False
    for root, _, files in os.walk("D:\\Bakend TrustShield"):
        for f in files:
            path = os.path.join(root, f)
            try:
                with open(path, "rb") as file_obj:
                    if target_bytes in file_obj.read():
                        disk_found = True
                        break
            except Exception:
                pass
    assert not disk_found


def test_temporary_state_cleanup():
    """12. DecodedAudio object garbage collection."""
    service = AudioDecoderService()
    wav_bytes = make_synthetic_wav_bytes(sample_rate=16000, channels=1, duration_seconds=0.5)
    decoded = service.decode_audio(wav_bytes)
    pcm_len = len(decoded.pcm_data)
    assert pcm_len == 16000  # 8000 samples * 2 bytes/sample
    del decoded
