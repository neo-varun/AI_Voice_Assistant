from openai import OpenAI

client = OpenAI()

LANGUAGE_NAMES = {
    'en': "English",
    'ta': "Tamil",
    'kn': "Kannada",
    'te': "Telugu",
    'ml': "Malayalam",
    'hi': "Hindi"
}

SYSTEM_PROMPT = """You are a sophisticated voice assistant who communicates as if you were a native {lang_name} speaker.
Speak in a warm, engaging tone and ask insightful follow-up questions when necessary before drawing conclusions.
Your responses should be articulate, nuanced, and rich in context.

When continuing a conversation:
1. Reference relevant information from previous exchanges
2. Ask follow-up questions when more information is needed
3. Explore topics in depth based on the user's interests
4. Don't repeat questions you've already asked
5. Remember personal details the user has shared

IMPORTANT:
- Respond exclusively in {lang_name}.
- Use clear, conversational language with impeccable grammar and a well-chosen vocabulary.
- Avoid special characters, extraneous formatting, or symbols.
- Keep your answers natural, engaging, and easy to understand.
"""

TRANSLATION_PROMPT = """You are an expert translator fluent in both {src_lang_name} and {tgt_lang_name}.
Understand the user's message in {src_lang_name} and craft a response in {tgt_lang_name} that is elegant, natural, and expressive.
If needed, ask thoughtful clarifying questions before delivering your final answer.

When continuing a conversation:
1. Reference relevant information from previous exchanges
2. Ask follow-up questions when more information is needed
3. Explore topics in depth based on the user's interests
4. Don't repeat questions you've already asked
5. Remember personal details the user has shared

IMPORTANT:
- Use idiomatic, conversational language that reflects native fluency.
- Ensure your response is grammatically impeccable and contextually appropriate.
- Avoid special characters, unnecessary formatting, or symbols.
"""

def voice_assistant_response(transcript, language="en", output_language=None, conversation_history=None):
    try:
        output_language = output_language or language
        language = language if language in LANGUAGE_NAMES else "en"
        output_language = output_language if output_language in LANGUAGE_NAMES else "en"
        
        is_translation = language != output_language

        if is_translation:
            prompt_text = TRANSLATION_PROMPT.format(
                src_lang_name=LANGUAGE_NAMES[language],
                tgt_lang_name=LANGUAGE_NAMES[output_language]
            )
        else:
            prompt_text = SYSTEM_PROMPT.format(lang_name=LANGUAGE_NAMES[language])
        
        messages = []
        
        if (conversation_history and len(conversation_history) > 0 and 
            conversation_history[0]["role"] == "system" and 
            "previous exchanges" in conversation_history[0]["content"]):
            messages = conversation_history
            
            last_user_msg = None
            for msg in reversed(messages):
                if msg["role"] == "user":
                    last_user_msg = msg
                    break
            
            if not last_user_msg or last_user_msg["content"] != transcript:
                messages.append({"role": "user", "content": transcript})
                
        else:
            messages.append({"role": "system", "content": prompt_text})
            
            if conversation_history and len(conversation_history) > 0:
                for msg in conversation_history:
                    if msg not in messages:
                        messages.append(msg)
            
            last_user_msg = None
            for msg in reversed(messages):
                if msg["role"] == "user":
                    last_user_msg = msg
                    break
                    
            if not last_user_msg or last_user_msg["content"] != transcript:
                messages.append({"role": "user", "content": transcript})
        
        response = client.chat.completions.create(
            model="gpt-4o-mini-2024-07-18",
            messages=messages,
            temperature=0.7,
            max_tokens=1500
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        return f"Error: AI response generation failed: {str(e)}"