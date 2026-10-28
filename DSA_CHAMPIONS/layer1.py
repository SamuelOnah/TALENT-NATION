import json
import os
import time
from dotenv import load_dotenv
from openai import OpenAI  
from google import genai
from groq import Groq

load_dotenv()

FILE = "tickets.json"

def choose_ai_model():
    """Prompts the user to explicitly choose an AI provider with no default fallback."""
    print("\nSelect AI Provider:")
    print("1. Gemini")
    print("2. OpenRouter")
    print("3. Groq")
    
    while True:
        choice = input("Enter choice (1, 2, or 3): ").strip()
        if choice == "1":
            return "gemini"
        elif choice == "2":
            return "openrouter"
        elif choice == "3":
            return "groq"
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")


def analyze_ticket_with_ai(description, provider):
    """Routes the ticket description to the selected AI provider."""
    prompt = f"Analyze this campus tech problem and suggest 3-4 concise ways to fix or investigate it: {description}"
    
    try:
        if provider == "gemini":
            client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
            
            for attempt in range(3):
                try:
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=prompt,
                    )
                    return response.text
                except Exception as e:
                    if attempt < 2:
                        time.sleep(2)
                        continue
                    raise e
            
        elif provider == "openrouter":
            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=os.environ.get("OPENROUTER_API_KEY")
            )
            response = client.chat.completions.create(
                model="openai/gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
            
        elif provider == "groq":
            client = Groq(
                api_key=os.environ.get("GROQ_API_KEY")
            )
            response = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
            
    except Exception as e:
        return f"Could not fetch AI suggestions from {provider.capitalize()}. (Error: {e})"


def create_ticket():
    title = input("Enter title: ").strip()
    description = input("Enter ticket description: ").strip()

    if not title or not description:
        print("Enter correct description")
        return 

    tickets = []

    if os.path.exists(FILE):
        try:
            with open(FILE, "r") as file:
                tickets = json.load(file)
        except (json.JSONDecodeError, OSError):
            print("Error: couldn't read tickets.json")
            tickets = []

    ticket_id = max(
        [t["id"] for t in tickets],
        default=0
    ) + 1

    tickets.append({
        "id": ticket_id,
        "title": title,
        "description": description
    })

    try:
        with open(FILE, "w") as file:
            json.dump(tickets, file, indent=4)

        print("Ticket created successfully.")
        print(f"\nID: {ticket_id}")
        print(f"Description: {description}")

        provider = choose_ai_model()
        print(f"\nGetting AI suggestions using {provider.capitalize()}...")
        
        ai_suggestion = analyze_ticket_with_ai(description, provider)
        print("\nSuggestions:")
        print(ai_suggestion)
        
    except OSError:
        print("Error: could not write to ticket")

if __name__ == "__main__":
    create_ticket()