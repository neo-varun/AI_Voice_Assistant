import logging
from openai import OpenAI

client = OpenAI()

def voice_assistant_response(transcript):

    prompt_text = (
        f"You are an advanced, friendly voice assistant that can help with any task through conversation only.\n"
        f"The user said: {transcript}\n\n"
        "Your job is to provide helpful, informative responses to any question or request. "
        "Before arriving at a final conclusion, ask follow-up questions to clarify the user's request. "
        "You decide how many questions are necessary - this depends entirely on your judgment of what information is needed. "
        "Only when you have gathered sufficient information should you provide a final answer. "
        "You only need to provide verbal assistance - no other actions are required beyond conversation. "
        "Keep your responses natural and conversational, as if you're having a friendly chat."
    )
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini-2024-07-18",
            messages=[
                {
                    "role": "system",
                    "content": "You are an advanced voice assistant who asks follow-up questions before providing conclusions. The number of questions needed is entirely your decision. Speak naturally and clearly."
                },
                {"role": "user", "content": prompt_text}
            ],
            temperature=0.3,
            max_tokens=1500
        )
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        logging.error(f"Error generating voice assistant response: {str(e)}")