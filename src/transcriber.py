from faster_whisper import WhisperModel
import os
from src.utils import format_timestamp

def transcribe(audio_path, cleanup_temp=True):
    # Load the model
    model = WhisperModel("base")

    # Transcribe the audio
    segments, info = model.transcribe(audio_path, beam_size=5, language="en")

    # Collect segments with formatted timestamps
    transcription_data = []
    for segment in segments:
        transcription_data.append({
            "start": format_timestamp(segment.start),
            "end": format_timestamp(segment.end),
            "text": segment.text
        })

    # Optionally delete the temp audio file
    if cleanup_temp:
        try:
            os.remove(audio_path)
        except Exception as e:
            print(f"Warning: Could not delete temp file {audio_path}: {e}")

    # Return the transcription data in memory
    return transcription_data
