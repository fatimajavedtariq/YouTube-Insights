import streamlit as st
from src.downloader import download_youtube_audio
from src.utils import is_valid_youtube_url
from src.transcriber import transcribe
from src.embeddings import create_vectorstore_from_transcription

def main():
    st.title("YouTube Insights")
    url = st.text_input("Enter your YouTube video URL:")

    if st.button("Analyze"):
        if is_valid_youtube_url(url):
            try:
                path = download_youtube_audio(url)
                st.success(f"Audio downloaded successfully: {path}")
                try:
                    transcription_data = transcribe(path)
                    st.success("Transcription completed successfully.")

                    # Create embeddings and vectorstore in memory
                    vectorstore = create_vectorstore_from_transcription(transcription_data)
                    st.success("Embeddings created and stored in vectorstore (in memory).")

                    # Optionally, show a sample of the transcript
                    st.subheader("Sample Transcript")
                    for segment in transcription_data[:5]:
                        st.write(f"{segment['start']} - {segment['end']}: {segment['text']}")

                except Exception as e:
                    st.error(f"Error during transcription: {e}")
            except Exception as e:
                st.error(f"Error downloading audio: {e}")
        else:
            st.error("Please enter a valid YouTube video URL.")

if __name__ == "__main__":
    main()