import os
import shutil
import streamlit as st
from src.utils import is_valid_youtube_url
from src.downloader import download_youtube_audio
from src.transcriber import transcribe
from src.embeddings import create_vectorstore_from_transcription
from src.qa_chain import create_qa_chain

def process_video(url, API_KEY, use_openai_whisper):
  with st.sidebar:
    if not is_valid_youtube_url(url):
        st.error("❌ Invalid YouTube URL. Please check and try again.")
        return

    st.info("🚀 Processing started")

    try:
        # Step 1: Download
        with st.spinner("📥 Step 1/3: Downloading audio..."):
            path, metadata, tmpdir = download_youtube_audio(url)
            st.session_state.metadata = metadata
            st.success("✅ Audio downloaded successfully.")

        # Step 2: Transcribe
        with st.spinner("📝 Step 2/3: Transcribing audio..."):
            try:
                st.session_state.transcription_data = transcribe(
                    path,
                    apikey=API_KEY if use_openai_whisper else None,
                    use_openai_whisper=use_openai_whisper
                )
                st.success("✅ Transcription completed.")
            except Exception as e:
                st.error(f"❌ Transcription failed: {str(e)}")
                raise
            finally:
                if os.path.exists(tmpdir):
                    shutil.rmtree(tmpdir, ignore_errors=True)

        # Step 3: Embeddings
        with st.spinner("🧠 Step 3/3: Creating embeddings..."):
            st.session_state.vectorstore = create_vectorstore_from_transcription(
                st.session_state.transcription_data,
                st.session_state.metadata
            )
            st.success("✅ Embeddings created and ready to use.")

        # Create QA Chain
        st.session_state.qa_chain = create_qa_chain(
            st.session_state.vectorstore,
            st.session_state.metadata, 
            api_key=API_KEY
        )
        st.success("🔗 QA Chain created successfully.")

    except Exception as e:
        st.error(f"⚠️ An error occurred: {str(e)}")
