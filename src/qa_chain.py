from langchain.prompts.chat import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory

def create_qa_chain(vectorstore, metadata, api_key=None):
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        openai_api_key=api_key,
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
    You are a helpful, conversational assistant that answers questions about a YouTube video using its metadata and transcript.

    Context includes:
    - Metadata: {metadata_context.strip()}
    - Transcript segments contain:
    • start time (mm:ss)
    • end time (mm:ss)
    • text (spoken content)

    Response Rules:

    A. Metadata questions (title/URL/uploader/description):
    1. Return exact values from metadata with no changes or paraphrasing.

    B. "When/where is [topic] discussed" questions:
    1. Find ALL relevant transcript segments in chronological order.
    2. Always use:
    - start and end for display.
    - int(start) for YouTube URL’s &t= parameter.
    3. Format each entry as:
    At [start]-[end]: [Brief context] (Watch at {video_url}&t=[int(start)]s)
    4. For follow-ups like "next time":
    - Continue numbering from the previous list.
    - Return the next chronological matches.

    C. "What is [topic]" questions:
    1. Identify segments where the topic is explained or defined.
    2. Summarize the explanation exactly as given in the video — do not add outside knowledge.
    3. Include the first relevant timestamp where it is discussed in the format:
    "[Summary of explanation] (Watch at {video_url}&t=[int(start)]s)"
    4. If multiple explanations appear, list them in chronological order with their timestamps.

    D. General rules:
    1. Keep responses conversational but precise with timestamps.
    2. Never merge different segments unless they overlap directly — each gets its own numbered entry.
    3. If topic not found, reply with:
    - "The video does not cover this topic." OR
    - "I don’t have information on this in the video."
    4. Never fabricate or infer beyond the transcript.
    5. Vary sentence structures to keep responses natural.

    E. Special handling:
    1. Merge overlapping segments into a continuous timestamp range.
    2. Store remaining matches for possible follow-up queries.
    3. Show timestamps naturally (e.g., "at 1:23") without decimal seconds.

    Example for "when is AI discussed?":
    1. At 0:15-0:45: Introduction to AI concepts (Watch at {video_url}&t=15s)
    2. At 2:30-3:15: Discussion of AI applications (Watch at {video_url}&t=150s)
    3. At 5:20-6:00: Future of AI technology (Watch at {video_url}&t=320s)

    Example for "what is AI?":
    AI is explained as a set of technologies that enable machines to perform tasks that typically require human intelligence. (Watch at {video_url}&t=15s)

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
