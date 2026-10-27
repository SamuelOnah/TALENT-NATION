import json
import os
from google import genai

FILE = "tickets.json"


def analyze_ticket_with_ai(description):
    try:
        client = genai.Client()

        prompt = f"Analyze this campus tech problem and suggest 3-4 concise ways to fix or investigate it:{description}"

        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt,
        )
        return response.text
    except Exception as e:
        return f"Could not fetch AI suggestions a this time. (Error: {e})"

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
        print(f"Ticket created successfully! {FILE}")

        print("\Getting AI suggestions...")
        ai_suggestion = analyze_ticket_with_ai(description)
        print("\nAI suggestions:")
        print(ai_suggestion)        
    except OSError:
        print("Error: could not write to ticket file")

if __name__ == "__main__":
    create_ticket()