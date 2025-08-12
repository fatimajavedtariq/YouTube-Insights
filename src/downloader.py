import os
import yt_dlp
import tempfile
import shutil

def download_youtube_audio(url):
    tmpdir = tempfile.mkdtemp()

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(tmpdir, '%(title)s.%(ext)s'),
        'restrictfilenames': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
        }],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        file_path = ydl.prepare_filename(info)  # This gets the actual file path
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
