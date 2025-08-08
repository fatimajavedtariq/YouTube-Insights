import os
import yt_dlp

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