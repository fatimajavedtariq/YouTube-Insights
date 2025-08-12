from langchain.prompts.chat import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory

def create_qa_chain(vectorstore, metadata):
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0.3,
        max_tokens=1500
    )

    video_url = metadata.get("webpage_url", "N/A")

    metadata_context = f"""
Title: {metadata.get("title", "Untitled")}
Description: {metadata.get("description", "No description available")}
Uploader: {metadata.get("uploader", "Unknown")}
URL: {metadata.get("webpage_url", "No URL available")}
Upload Date: {metadata.get("upload_date", "Unknown")}
"""

    system_prompt = f"""
You are a helpful, conversational assistant that answers questions about a YouTube video using its transcript and metadata.

Context includes:
- Metadata: {metadata_context.strip()}
- Transcript segments: start time, end time, and spoken text.

Rules:
1. If the user asks about the video title, url, uploader, description, return it exactly from metadata.
2. If the user asks about something that happens at a certain time, use semantic search to find the relevant transcript segments and return the video url along with it too.
3. Merge overlapping or closely timed segments into one continuous range.
4. Present the answer in friendly, natural language, explaining the context briefly.
5. At the end, provide one clickable YouTube link to the first relevant moment using this exact format:
   {video_url}&t=<start_seconds>s
6. If multiple distinct moments are relevant, list them in chronological order, each with its own clickable timestamp in the same format.
7. Never make up information — if something is not in the transcript or metadata, say "I don't know."
8. Avoid repeating identical sentence patterns in consecutive answers.
9. Do not restate the user's question in the answer unless necessary for clarity.
context: {{context}}
"""

    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(system_prompt),
        HumanMessagePromptTemplate.from_template("{question}")
    ])

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
    )

    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory,
        combine_docs_chain_kwargs={
            "prompt": prompt,
            "document_variable_name": "context"
        },
    )

    return chain
