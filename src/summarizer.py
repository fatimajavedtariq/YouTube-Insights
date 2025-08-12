from openai import OpenAI

def summarize_transcription(transcription_data, video_title=None, api_key=None):
    client = OpenAI()
    system_prompt = "You are a helpful assistant that summarizes transcripts."
    
    user_prompt = f"""
You are an expert content summarizer.
Your task is to read the following YouTube video transcription and produce a **clear, concise, and engaging summary** of the video.

Video Title: {video_title if video_title else 'Untitled'}

Full Transcription:
{transcription_data}

Guidelines:
- Start the summary with 1–2 sentences giving the overall theme of the video.
- Then list 3–6 bullet points capturing the main topics or arguments in order of appearance.
- Do not include filler words, irrelevant tangents, or repeated phrases.
- Keep the tone neutral and informative.
- The summary should be understandable even without watching the video.
- Maximum length: 200 words.

Return only the summary, without extra explanations or notes.
"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3
    )
    return response.choices[0].message.content.strip()
