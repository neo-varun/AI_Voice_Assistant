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

SYSTEM_PROMPT = 'Voice assistant speaking fluent {lang_name}. IMPORTANT: Outputs will be spoken aloud, so never use asterisks (*,-) or any text formatting. Use natural words, be warm, ask follow-up questions, reference previous exchanges.'

TRANSLATION_PROMPT = 'Translator speaking fluent {tgt_lang_name}. IMPORTANT: Outputs will be spoken aloud, so never use asterisks (*,-) or any text formatting. Understand in {src_lang_name}, respond in {tgt_lang_name} naturally. Ask clarifying questions if needed.'

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