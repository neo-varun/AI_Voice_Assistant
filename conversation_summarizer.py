from openai import OpenAI

client = OpenAI()

def summarize_exchange(exchange):
    messages = [
        {"role": "system", "content": """Summarize this exchange in exactly TWO lines:
         Line 1: What the user said/asked (under 15 words)
         Line 2: How the assistant responded (under 15 words)"""},
        {"role": "user", "content": "Summarize:"}
    ]
    
    messages.extend(exchange)
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini-2024-07-18",
            messages=messages,
            temperature=0.3,
            max_tokens=100
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating summary: {str(e)}"

class ConversationManager:
    def __init__(self):
        self.conversations = {}
    
    def add_exchange(self, session_id, user_message, assistant_message):
        if session_id not in self.conversations:
            self.conversations[session_id] = {"summaries": [], "latest": []}
        
        exchange = [
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": assistant_message}
        ]
        
        self.conversations[session_id]["latest"] = exchange
        
        summary = summarize_exchange(exchange)
        self.conversations[session_id]["summaries"].append(
            {"role": "system", "content": f"EXCHANGE: {summary}"}
        )
        
        return self.conversations[session_id]
    
    def get_summary(self, session_id):
        if session_id not in self.conversations:
            return "No conversation found."
        
        return "\n".join([item["content"].replace("EXCHANGE: ", "") 
                          for item in self.conversations[session_id]["summaries"]])
    
    def get_context_with_summary(self, session_id):
        if session_id not in self.conversations:
            return []
        
        context = []
        summaries = self.conversations[session_id]["summaries"]
        
        if summaries:
            context.append({
                "role": "system", 
                "content": "Previous exchanges summarized below. Continue based on these and recent messages."
            })
            context.extend(summaries)
        
        if self.conversations[session_id]["latest"]:
            context.extend(self.conversations[session_id]["latest"])
        
        return context 