import json
import os
from google import genai
import time


FILE = "tickets.json"

def choose_ai_model():
    print("\nSelect AI Provider:")
    print("1. Gemini")
    print("2. OpenRouter")
    print("3. Grok")
    
    choice = input("Enter choice (1-3, default 1): ").strip()
    
    if choice == "2":
        return "openrouter"
    elif choice == "3":
        return "grok"
    else:
        return "gemini"

def analyze_ticket_with_ai(description):
    client = genai.Client()
    prompt = f"Analyze this campus tech problem and suggest 3-4 concise ways to fix or investigate it: {description}"
    
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model='gemini-3.8-flash',
                contents=prompt,
            )
            return response.text
        except Exception as e:

            if "503" in str(e) and attempt < 2:
                time.sleep(2)
                continue
            return f"Could not fetch AI suggestions at this time. (Error: {e})"

def create_ticket():
    title =  input("Enter title: ").strip()
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
            print("Error: could'nt read tickets.json")
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

        print("\nGetting AI suggestions...")
        ai_suggestion = analyze_ticket_with_ai(description)
        print("suggestions:")
        print(ai_suggestion)        
    except OSError:
        print("Error: could not write to ticket")

if __name__ == "__main__":
    create_ticket()