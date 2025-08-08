import os
import yt_dlp
import tempfile
import shutil

def download_youtube_audio(url):
   with tempfile.TemporaryDirectory() as tmpdir:
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(tmpdir, '%(title)s.%(ext)s'),
        """'external_downloader': 'aria2c',
        'external_downloader_args': ['-x', '16', '-k', '1M'],"""
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
            filename = None

        if filename:
          temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
          shutil.copyfile(filename, temp_audio.name)
          return temp_audio.name
        else:
            raise Exception("Audio file not found.")