import os
import yt_dlp
import tempfile
import shutil
import traceback

def download_youtube_audio(url):
    tmpdir = tempfile.mkdtemp()

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(tmpdir, "%(title)s.%(ext)s"),
        "restrictfilenames": True,
        "noplaylist": True,
        "ignoreerrors": True,
        "quiet": True,
        "no_warnings": True,
        "geo_bypass": True,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

            if not info:
                raise ValueError("Failed to retrieve video info. Possibly private, age-restricted, or geo-blocked.")

            file_path = ydl.prepare_filename(info)
            file_path = os.path.splitext(file_path)[0] + ".mp3"  # ensure mp3

        metadata = {
            "title": info.get("title"),
            "description": info.get("description"),
            "uploader": info.get("uploader"),
            "upload_date": info.get("upload_date"),
            "duration": info.get("duration"),
            "view_count": info.get("view_count"),
            "like_count": info.get("like_count"),
            "channel_id": info.get("channel_id"),
            "webpage_url": info.get("webpage_url"),
        }

        return file_path, metadata, tmpdir

    except Exception as e:
        # Print full error to logs (so Streamlit doesn't redact it)
        print("yt_dlp download error:", traceback.format_exc())
        shutil.rmtree(tmpdir, ignore_errors=True)
        raise
