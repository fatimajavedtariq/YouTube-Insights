from faster_whisper import WhisperModel
import os
import json
from src.utils import format_timestamp

def transcribe(audio_path, output_dir="transcriptions", cleanup_temp=True):
    os.makedirs(output_dir, exist_ok=True)

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

    # Save to file
    base_name = os.path.basename(audio_path).split('.')[0]
    output_path = os.path.join(output_dir, f"{base_name}.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(transcription_data, f, indent=2, ensure_ascii=False)

    print(f"Transcription saved to {output_path}")

    # Optionally delete the temp audio file
    if cleanup_temp:
        try:
            os.remove(audio_path)
        except Exception as e:
            print(f"Warning: Could not delete temp file {audio_path}: {e}")

    return output_path
