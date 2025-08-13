from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

def summarize_transcription(transcription_data, video_title=None, api_key=None):
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0.3,
        api_key=api_key
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant that summarizes transcripts."),
        ("user", """
You are an expert content summarizer.
Video Title: {video_title}

Full Transcription:
{transcription_data}

Guidelines:
- Summarize the main points of the video
-Mentiion the title of the video
- Start with 1–2 sentences on overall theme
- Then list 3–6 bullet points in order of appearance
- No filler words, irrelevant tangents, or repeated phrases
- Max 200 words
Return only the summary.
""")
    ])

    chain = prompt | llm
    
    return chain.invoke({
        "video_title": video_title or "Untitled",
        "transcription_data": transcription_data
    }).content.strip()
