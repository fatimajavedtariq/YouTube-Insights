from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document

def create_vectorstore_from_transcription(transcription_data, metadata):
    docs = []

    docs.append(Document(
        page_content=(
            f"Title: {metadata.get('title', '')}\n"
            f"Description: {metadata.get('description', '')}\n"
            f"Uploader: {metadata.get('uploader', '')}\n"
            f"URL: {metadata.get('webpage_url', '')}"
        ),
        metadata={"type": "video_metadata"}
    ))
    
    for idx, seg in enumerate(transcription_data):
        if seg.get("text") and seg["text"].strip():
            start_ts = seg['start']
            end_ts = seg['end']
            text_with_ts = f"[{start_ts} - {end_ts}] {seg['text'].strip()}"

            docs.append(Document(
                page_content=text_with_ts,
                metadata={"type": "transcript", "index": idx}
            ))

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = FAISS.from_documents(docs, embedding=embeddings)

    return vectorstore
