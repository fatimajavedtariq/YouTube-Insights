from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings  # Use HuggingFace embeddings

def create_vectorstore_from_transcription(transcription_data):
    """
    transcription_data: list of dicts with 'start', 'end', 'text'
    Returns an in-memory FAISS vectorstore.
    """
    # Prepare documents with timestamps preserved
    documents = [
        f"{segment['start']} --> {segment['end']} | {segment['text']}"
        for segment in transcription_data
    ]

    # Create embeddings and vector store in memory using HuggingFace
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = FAISS.from_texts(documents, embedding=embeddings)

    return vectorstore