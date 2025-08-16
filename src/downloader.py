import os
import yt_dlp
import tempfile
import shutil
import streamlit as st

def download_youtube_audio(url):
    tmpdir = tempfile.mkdtemp()

    # Load cookies from Streamlit secrets
    cookies_path = None
    if "cookies" in st.secrets:
        cookies_path = os.path.join(tmpdir, "cookies.txt")
        with open(cookies_path, "w", encoding="utf-8") as f:
            f.write(st.secrets["cookies"])

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(tmpdir, '%(title)s.%(ext)s'),
        'restrictfilenames': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
        }],
    }

    # If cookies exist, add to yt-dlp opts
    if cookies_path:
        ydl_opts['cookiefile'] = cookies_path

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        file_path = ydl.prepare_filename(info)  # Actual file path
        file_path = os.path.splitext(file_path)[0] + ".mp3"  # Ensure mp3 extension

    metadata = {
        "title": info.get("title"),
        "description": info.get("description"),
        "uploader": info.get("uploader"),
        "upload_date": info.get("upload_date"),
        "duration": info.get("duration"),
        "view_count": info.get("view_count"),
        "like_count": info.get("like_count"),
        "channel_id": info.get("channel_id"),
        "webpage_url": info.get("webpage_url")
    }

    return file_path, metadata, tmpdir
