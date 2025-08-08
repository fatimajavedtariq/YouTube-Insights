import streamlit as st
import re
import yt_dlp
import os
from faster_whisper import WhisperModel
from dotenv import load_dotenv

import os
from openai import OpenAI
import json
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
load_dotenv()
client = OpenAI()
def is_valid_youtube_url(url):
    pattern = r'^https?://(www\.)?(youtube\.com/watch\?v=|youtu\.be/)[\w-]{11}($|[&?])'
    return re.match(pattern, url) is not None

def download_youtube_audio(url, output_path='downloads'):
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'external_downloader': 'aria2c',
        'external_downloader_args': ['-x', '16', '-k', '1M'],
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',            
        }],
        'quiet': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        # Find the actual output file after postprocessing
        if 'requested_downloads' in info and info['requested_downloads']:
            filename = info['requested_downloads'][0]['filepath']
        elif '_filename' in info:
            filename = info['_filename']
        else:
            # fallback: try to construct filename
            filename = os.path.join(output_path, info['title'].replace(" ", "_") + ".mp3")
        return filename

def transcribe_and_embed(file_path, output_dir="transcriptions", faiss_dir="faiss_index"):
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(faiss_dir, exist_ok=True)

    # Transcribe with Whisper (OpenAI API)
    with open(file_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="verbose_json",
        )

    # Save transcription
    transcript_dict = transcript.model_dump()
    transcript_path = os.path.join(output_dir, os.path.basename(file_path) + ".json")
    with open(transcript_path, "w", encoding="utf-8") as f:
        json.dump(transcript_dict, f, ensure_ascii=False, indent=2)

    # Prepare timestamped chunks
    segments = transcript_dict["segments"]
    documents = [
        f"{seg['start']} --> {seg['end']} | {seg['text']}" for seg in segments
    ]

    # Create embeddings
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_texts(documents, embedding=embeddings)

    # Save FAISS index
    faiss_path = os.path.join(faiss_dir, os.path.basename(file_path))
    vectorstore.save_local(faiss_path)

    return vectorstore, transcript_dict, faiss_path


def format_timestamp(seconds):
    minutes, secs = divmod(int(seconds), 60)
    return f"{minutes}:{secs:02d}"

def main():
    st.title("YouTube Insights")
    url = st.text_input("Enter your YouTube video URL:")

    if st.button("Analyze"):
        if is_valid_youtube_url(url):
            try:
                path = download_youtube_audio(url)
                st.success(f"Audio downloaded successfully: {path}")
                try:
                    vectorstore, transcript, faiss_path = transcribe_and_embed(path)
                    st.success("Transcription completed successfully.")

                    # Show part of transcript with MM:SS timestamps
                    st.subheader("Sample Transcript")
                    for segment in transcript["segments"][:5]:
                        start = format_timestamp(segment["start"])
                        end = format_timestamp(segment["end"])
                        st.write(f"{start} - {end}: {segment['text']}")

                except Exception as e:
                    st.error(f"Error during transcription: {e}")
            except Exception as e:
                st.error(f"Error downloading audio: {e}")
        else:
            st.error("Please enter a valid YouTube video URL.")

if __name__ == "__main__":
    main()