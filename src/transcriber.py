from faster_whisper import WhisperModel
import streamlit as st
from openai import OpenAI
from src.utils import format_timestamp

def transcribe(audio_path, apikey=None, use_openai_whisper=False, cleanup_temp=True):
    if use_openai_whisper:
        if not apikey:
            raise ValueError("OpenAI API key is required for Whisper API")
        
        # Use OpenAI Whisper API (paid)
        client = OpenAI(api_key=apikey)
        
        with open(audio_path, "rb") as audio_file:
            response = client.audio.transcriptions.create(
                file=audio_file,
                model="whisper-1",
                response_format="verbose_json"
            )
        transcription_data = []
        for segment in response.segments:
            transcription_data.append({
                "start": format_timestamp(segment.start),
                "end": format_timestamp(segment.end),
                "text": segment.text
            })
    else:
        st.info("Using local faster_whisper for transcription (free option)")     
        model = WhisperModel("base")
        segments, info = model.transcribe(audio_path, beam_size=5, language="en")

        transcription_data = []
        for segment in segments:
            transcription_data.append({
                "start": format_timestamp(segment.start),
                "end": format_timestamp(segment.end),
                "text": segment.text
            })


    return transcription_data