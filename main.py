import streamlit as st
from src.downloader import download_youtube_audio
from src.utils import is_valid_youtube_url
from src.transcriber import transcribe
from src.embeddings import create_vectorstore_from_transcription
from src.summarizer import summarize_transcription
from src.qa_chain import create_qa_chain
import shutil
import os

def main():
    st.set_page_config(layout="wide")
    st.markdown("""
    <style>
        .block-container {
            padding-top: 1rem;
        }
    </style>
    """, unsafe_allow_html=True)

    st.title("YouTube Insights")
    st.sidebar.title("🔑 Configuration")

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "vectorstore" not in st.session_state:
        st.session_state.vectorstore = None
    if "qa_chain" not in st.session_state:
        st.session_state.qa_chain = None
    if "transcription_data" not in st.session_state:
        st.session_state.transcription_data = None
    if "memory" not in st.session_state:
        st.session_state.memory = None
    if "metadata" not in st.session_state:
        st.session_state.metadata = None
    with st.sidebar:
            url = st.text_input("Enter YouTube Video URL", placeholder="https://www.youtube.com/watch?v=example")
            API_KEY = st.text_input("OpenAI API Key", type="password", placeholder="sk-...")
            use_openai_whisper = st.checkbox("Use OpenAI Whisper for transcription (more accurate)", value=False)
            process_button = st.button(
                "Process Video",
                disabled=not (url and API_KEY),
                help="Enter URL and API Key to enable"
            )


    with st.sidebar:
        if process_button and st.session_state.vectorstore is None:
            if url and API_KEY:  
                if is_valid_youtube_url(url):
                    try:
                        if st.session_state.vectorstore is None:
                            st.info("🚀 Processing started")
                            with st.spinner("📥 Step 1/3: Downloading audio..."):
                                path, metadata, tmpdir = download_youtube_audio(url)
                                st.session_state.metadata = metadata
                                st.success("✅ Audio downloaded successfully.")
                            with st.spinner("📝 Step 2/3: Transcribing audio..."):
                                try:
                                    st.session_state.transcription_data = transcribe(path, apikey=API_KEY if use_openai_whisper else None,
        use_openai_whisper=use_openai_whisper)
                                    st.success("✅ Transcription completed.")
                                except Exception as e:
                                    st.error(f"❌ Transcription failed: {str(e)}")
                                    raise
                                finally:
                                    if os.path.exists(tmpdir):
                                        shutil.rmtree(tmpdir, ignore_errors=True)

                            with st.spinner("🧠 Step 3/3: Creating embeddings..."):
                                st.session_state.vectorstore = create_vectorstore_from_transcription(
                                    st.session_state.transcription_data,
                                    st.session_state.metadata,
                                )
                                st.success("✅ Embeddings created and ready to use.")

                            st.session_state.qa_chain = create_qa_chain(st.session_state.vectorstore, st.session_state.metadata)
                            st.success("🔗 QA Chain created successfully.")
                    except Exception as e:
                        st.error(f"⚠️ An error occurred: {str(e)}")
                else:
                    st.error("❌ Invalid YouTube URL. Please check and try again.")
            elif url and not API_KEY:
                st.error("❌ Please enter your OpenAI API key")
            else:
                st.info("ℹ️ Please enter a YouTube video URL to begin.")
                
    if st.session_state.transcription_data is not None:
        with st.expander("VideoSummary", expanded=False):
                if st.session_state.memory is None:
                    with st.spinner("Generating summary..."):
                        try:                            
                            st.session_state.memory = summarize_transcription(
                                st.session_state.transcription_data,
                                st.session_state.metadata.get("title"),
                                api_key=API_KEY
                            )
                        except Exception as e:
                            st.error(f"Error generating summary: {str(e)}")
                            st.session_state.memory = "Summary unavailable"
                st.write(st.session_state.memory)


    st.subheader("🎯 YouTube QA Chatbot")
    if st.session_state.qa_chain is None:
        st.warning("Please process a video first to enable the chatbot.")
    else:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        if prompt := st.chat_input("Ask something about the video..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            if st.session_state.qa_chain and API_KEY:
                try:
                    result = st.session_state.qa_chain({"question": prompt, "chat_history": st.session_state.messages})
                    result = result['answer'] if isinstance(result, dict) else result
                    st.session_state.messages.append({"role": "assistant", "content": result})
                    st.rerun() 
                except Exception as e:
                    st.error(f"Error generating response: {str(e)}")
            
    
if __name__ == "__main__":
    main()