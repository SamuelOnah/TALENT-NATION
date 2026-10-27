import json
import os


FILE = "tickets.json"

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
    except OSError:
        print("Error: could not read ticket")

if __name__ == "__main__":
    create_ticket()