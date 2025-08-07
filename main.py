import streamlit as st
import re
import yt_dlp
import os


def is_valid_youtube_url(url):
    pattern = r'^https?://(www\.)?(youtube\.com/watch\?v=|youtu\.be/)[\w-]{11}($|[&?])'
    return re.match(pattern, url) is not None

def download_youtube_audio(url, output_path='downloads'):
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
        }],
        'quiet': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = info['title'].replace(" ", "_") + ".mp3"
        return os.path.join(output_path, filename)

    
def main():
    st.title("YouTube Insights")
    url = st.text_input("Enter your YouTube video URL:")
    
    if st.button("Analyze"):
        if is_valid_youtube_url(url):
            try:
                path = download_youtube_audio(url)
                st.success(f"Audio downloaded successfully: {path}")
            except Exception as e:
                st.error(f"Error downloading audio: {e}")
        else:
            st.error("Please enter a valid YouTube video URL.")
            
if __name__ == "__main__":
    main()