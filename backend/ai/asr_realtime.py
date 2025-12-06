# backend/ai/asr_realtime.py

import json
import queue
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import soundfile as sf
import sounddevice as sd
import torch
from faster_whisper import WhisperModel

from summarizer import summarize_conversation  # our other file

# ================== CONFIG ==================
SAMPLE_RATE = 16000
CHUNK_SIZE = 1024
VAD_THRESHOLD = 0.0008      # energy threshold
SILENCE_LIMIT = 10.0        # seconds of silence to stop
MODEL_SIZE = "medium"

BASE_DIR = Path(__file__).resolve().parent.parent  # backend/
MODEL_DIR = BASE_DIR / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

RECORDINGS_DIR = BASE_DIR / "recordings"
RECORDINGS_DIR.mkdir(parents=True, exist_ok=True)

WHISPER_CACHE_DIR = MODEL_DIR / "whisper_cache"
WHISPER_CACHE_DIR.mkdir(parents=True, exist_ok=True)

# ================== HELPER FUNCTIONS ==================
def vad_is_speech(audio_chunk: np.ndarray) -> bool:
    """
    Simple energy-based VAD.
    """
    energy = np.mean(audio_chunk ** 2)
    return energy > VAD_THRESHOLD

# ================== LOAD WHISPER MODEL ==================
if torch.cuda.is_available():
    stt_model = WhisperModel(
        MODEL_SIZE,
        device="cuda",
        compute_type="float16",
        download_root=str(WHISPER_CACHE_DIR),
    )
    print("Whisper using GPU")
else:
    stt_model = WhisperModel(
        MODEL_SIZE,
        device="cpu",
        compute_type="int8",
        download_root=str(WHISPER_CACHE_DIR),
    )
    print("✅ Whisper using CPU")

audio_q = queue.Queue()

def audio_callback(indata, frames, time_info, status):
    if status:
        print("⚠️", status)
    audio_q.put(indata.copy())

# ================== MAIN PIPELINE ==================
def run_realtime_once():
    """
    Record one conversation until 10 seconds of silence,
    transcribe the full audio once at the end,
    and return the transcript string.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    wav_path = RECORDINGS_DIR / f"convo_{timestamp}.wav"

    recorded_chunks = []
    silence_time = 0.0
    started_talking = False

    try:
        with sd.InputStream(
            samplerate=SAMPLE_RATE,
            blocksize=CHUNK_SIZE,
            channels=1,
            dtype="float32",
            callback=audio_callback,
        ):
            # print("🎙 Listening... speak normally. Auto-stops after silence.")

            last_chunk_time = time.time()

            while True:
                try:
                    chunk = audio_q.get(timeout=1.0)
                except queue.Empty:
                    # no audio => keep waiting
                    continue

                if chunk.ndim > 1:
                    chunk = chunk[:, 0]

                recorded_chunks.append(chunk.copy())

                # VAD for silence detection
                if vad_is_speech(chunk):
                    started_talking = True
                    silence_time = 0.0
                else:
                    if started_talking:
                        silence_time += CHUNK_SIZE / SAMPLE_RATE
                        if silence_time >= SILENCE_LIMIT:
                            # print("🔚 Silence detected, stopping.")
                            break

    except KeyboardInterrupt:
        # print("🛑 Recording stopped manually.")
        pass

    if not recorded_chunks:
        return ""

    # Combine into single array
    audio_arr = np.concatenate(recorded_chunks, axis=0).astype(np.float32)
    sf.write(str(wav_path), audio_arr, SAMPLE_RATE)

    # Transcribe full audio
    segments, _ = stt_model.transcribe(
        audio_arr, beam_size=5, language="en", vad_filter=True
    )
    transcript = " ".join(seg.text.strip() for seg in segments).strip()
    return transcript


def main():
    transcript = run_realtime_once().strip()

    if not transcript:
        # No audio or nothing spoken
        result = {
            "error": "No transcript captured",
            "transcript": "",
            "summary": "",
        }
        print(json.dumps(result), end="")
        return

    summary = summarize_conversation(transcript)

    result = {
        "transcript": transcript,
        "summary": summary,
    }

    # 🔴 IMPORTANT: Node will read this JSON from stdout
    print(json.dumps(result), end="")


if __name__ == "__main__":
    main()
