import os
import shutil
import streamlit as st
from src.pipeline import process_video
from src.summarizer import summarize_transcription

def main():
    # Page config
    st.set_page_config(layout="wide")
    st.markdown("""
    <style>.block-container { padding-top: 1rem; }</style>
    """, unsafe_allow_html=True)

    st.title("YouTube Insights")
    st.sidebar.title("🔑 Configuration")

    # Session state setup
    for key in ["messages", "vectorstore", "qa_chain", "transcription_data", "memory", "metadata", "transcription"]:
        if key not in st.session_state:
            st.session_state[key] = [] if key == "messages" else None

    # Sidebar inputs
    url = st.sidebar.text_input("YouTube Video URL", placeholder="https://www.youtube.com/watch?v=example")
    st.session_state.API_KEY = st.sidebar.text_input("OpenAI API Key", type="password", placeholder="sk-...")
    transcription_option = st.sidebar.radio(
    "Transcription Method",
    horizontal=True,
    help="Choose between local Whisper (free) or OpenAI Whisper (paid)",
    options=["Local Whisper", "OpenAI Whisper"]
)

    use_openai_whisper = transcription_option ==  "OpenAI Whisper"
    process_button = st.sidebar.button(
        "Process Video",
        disabled=not (url and st.session_state.API_KEY),
        help="Enter URL and API Key to enable",
        use_container_width=True
    )

    # Process video
    if process_button and st.session_state.vectorstore is None:
        process_video(url, st.session_state.API_KEY, use_openai_whisper)

    if st.session_state.transcription_data:
        with st.expander("Video Transcription", expanded=False):
            if "transcription" not in st.session_state:
                st.session_state.transcription = st.session_state.transcription_data
            
            for segment in st.session_state.transcription:
                start = segment['start']
                end = segment['end']
                st.markdown(f"**{start} - {end}**: {segment['text']}")

    # Show summary
    if st.session_state.transcription_data:
        with st.expander("Video Summary", expanded=False):
            if st.session_state.memory is None:
                with st.spinner("Generating summary..."):
                    try:
                        st.session_state.memory = summarize_transcription(
                            st.session_state.transcription_data,
                            st.session_state.metadata.get("title"),
                            api_key=st.session_state.API_KEY
                        )
                    except Exception as e:
                        st.error(f"Error generating summary: {str(e)}")
                        st.session_state.memory = "Summary unavailable"
            st.write(st.session_state.memory)

    # Chatbot section
    st.subheader("QA Chatbot")
    if st.session_state.qa_chain is None:
        st.warning("Please process a video first to enable the chatbot.")
    else:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Ask something about the video..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            try:
                result = st.session_state.qa_chain({
                    "question": prompt,
                    "chat_history": st.session_state.messages
                })
                answer = result['answer'] if isinstance(result, dict) else result
                st.session_state.messages.append({"role": "assistant", "content": answer})
                st.rerun()
            except Exception as e:
                st.error(f"Error generating response: {str(e)}")

if __name__ == "__main__":
    main()
