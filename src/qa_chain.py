from langchain.prompts.chat import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory

def create_qa_chain(vectorstore, metadata, api_key=None):
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        api_key=api_key,
        temperature=0.2,
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
1. If the user asks for the video title, URL, uploader, or description, return it exactly from metadata without modification.
2. If the user asks when a certain topic is discussed, search the transcript semantically for all relevant segments.
3. Return the earliest occurrence first, along with any closely overlapping segments merged into one continuous range.
4. Store all other distinct occurrences in chronological order for potential follow-up questions (e.g., "next time").
5. If the user later asks for the "next time" or "other times" the topic appears, provide the next occurrence(s) in order.
6. Always attach the video URL with the correct timestamp using this exact format:
   {video_url}&t=<start_time_in_seconds>s
7. When displaying timestamps to the user in natural language, convert seconds to hh:mm:ss format. Example: 125 → 00:02:05.
8. If multiple distinct moments are relevant, list them all in chronological order, each with its clickable timestamp.
9. Present answers in friendly, natural language, briefly explaining the context of the moment(s).
10. Never fabricate information. If not found in metadata or transcript, respond: "I don't know."
11. Avoid repeating identical sentence patterns in consecutive answers.

Context: {{context}}

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
