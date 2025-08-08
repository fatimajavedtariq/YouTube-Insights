import streamlit as st
from src.downloader import download_youtube_audio
from src.utils import is_valid_youtube_url
from src.transcriber import transcribe








def main():
    st.title("YouTube Insights")
    url = st.text_input("Enter your YouTube video URL:")

    if st.button("Analyze"):
        if is_valid_youtube_url(url):
            try:
                path = download_youtube_audio(url)
                st.write()
                st.success(f"Audio downloaded successfully: {path}")
                try:
                    transcribe(path)
                    st.success("Transcription completed successfully.")
                except Exception as e:
                    st.error(f"Error during transcription: {e}")
            except Exception as e:
                st.error(f"Error downloading audio: {e}")
        else:
            st.error("Please enter a valid YouTube video URL.")

if __name__ == "__main__":
    main()