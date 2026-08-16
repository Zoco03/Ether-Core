import os
import wave
import asyncio
import pyaudio
import edge_tts
from faster_whisper import WhisperModel

os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

# Load Whisper onto your RTX 4050 GPU using 8-bit quantization
stt_model = WhisperModel("distil-large-v3", device="cuda", compute_type="int8_float16")

def listen_to_user(record_seconds: int = 6) -> str:
    """Records microphone input and transcribes it locally using CUDA."""
    chunk = 1024
    audio_format = pyaudio.paInt16
    channels = 1
    rate = 16000
    temp_wav = "input_audio.wav"

    audio = pyaudio.PyAudio()
    stream = audio.open(
        format=audio_format,
        channels=channels,
        rate=rate,
        input=True,
        frames_per_buffer=chunk
    )

    print("\n* Listening... Speak your prompt.")
    frames = []

    for _ in range(0, int(rate / chunk * record_seconds)):
        data = stream.read(chunk)
        frames.append(data)

    print("* Processing voice...")
    stream.stop_stream()
    stream.close()
    audio.terminate()

    with wave.open(temp_wav, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(audio.get_sample_size(audio_format))
        wf.setframerate(rate)
        wf.writeframes(b''.join(frames))

    # Multilingual transcription (Whisper auto-detects language)
    segments, _ = stt_model.transcribe(temp_wav, beam_size=5)
    transcription = "".join([segment.text for segment in segments]).strip()

    return transcription

async def speak_to_user(text: str):
    """Converts the response text to spoken audio and plays it."""
    print(f"\n[Boss Model Output]:\n{text}\n")
    output_audio = "output_audio.mp3"
    
    communicate = edge_tts.Communicate(text, "en-US-ChristopherNeural")
    await communicate.save(output_audio)
    
    # Play audio on Windows
    os.system(f"start {output_audio}")