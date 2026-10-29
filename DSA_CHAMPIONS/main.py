import json
import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI
from google import genai
from groq import Groq

load_dotenv()
app = FastAPI(title="Campus Ticket Terminal Playground")

FILE = "tickets.json"

class CommandRequest(BaseModel):
    command: str
    provider: str = "gemini"

class TicketRequest(BaseModel):
    title: str
    description: str
    provider: str = "gemini"

def run_ai_analysis(description: str, provider: str) -> str:
    prompt = f"Analyze this campus tech problem and suggest 3-4 concise ways to fix or investigate it: {description}"
    try:
        if provider == "gemini":
            client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
            response = client.models.generate_content(
                model='gemini-3.8-flash',
                contents=prompt,
            )
            return response.text
        elif provider == "openrouter":
            client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.environ.get("OPENROUTER_API_KEY"))
            response = client.chat.completions.create(
                model="openai/gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        elif provider == "groq":
            client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
            response = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        else:
            return "Unknown provider."
    except Exception as e:
        return f"Error connecting to {provider}: {str(e)}"

@app.get("/", response_class=HTMLResponse)
def terminal_ui():
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Campus Ticket AI Playground</title>
    <style>
        body { background-color: #0d1117; color: #58a6ff; font-family: 'Courier New', Courier, monospace; margin: 0; padding: 20px; }
        .container { max-width: 950px; margin: auto; background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
        h1 { color: #f0f6fc; font-size: 1.5rem; margin-top: 0; border-bottom: 1px solid #30363d; padding-bottom: 10px; }
        
        .panel { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 15px; }
        @media (max-width: 768px) { .panel { grid-template-columns: 1fr; } }
        
        .form-group { display: flex; flex-direction: column; gap: 8px; background: #010409; padding: 15px; border-radius: 6px; border: 1px solid #30363d; }
        label { color: #f0f6fc; font-size: 0.9rem; font-weight: bold; }
        input, textarea, select { background: #0d1117; color: #c9d1d9; border: 1px solid #30363d; padding: 10px; border-radius: 6px; font-family: inherit; outline: none; }
        input:focus, textarea:focus, select:focus { border-color: #58a6ff; }
        textarea { resize: vertical; height: 80px; }
        
        button { background: #238636; color: white; border: none; padding: 10px; border-radius: 6px; font-weight: bold; cursor: pointer; font-family: inherit; transition: background 0.2s; }
        button:hover { background: #2ea043; }

        #output { height: 320px; overflow-y: auto; background: #010409; padding: 15px; border-radius: 6px; border: 1px solid #30363d; white-space: pre-wrap; font-size: 14px; line-height: 1.4; color: #c9d1d9; margin-bottom: 15px; }
        
        .cli-row { display: flex; gap: 10px; align-items: center; background: #010409; padding: 10px; border-radius: 6px; border: 1px solid #30363d; }
        .cli-row input { flex-grow: 1; border: none; background: transparent; color: #58a6ff; }
    </style>
</head>
<body>
    <div class="container">
        <h1>⚡ Campus Ticket AI Playground</h1>
        
        <!-- Top Output Screen -->
        <div id="output">Welcome to the Campus Ticket AI Playground!
Use the form below to submit a tech issue or type commands in the terminal bar.
</div>

        <!-- Input Panel: Easy Form -->
        <div class="panel">
            <div class="form-group">
                <label for="ticketTitle">Ticket Title</label>
                <input type="text" id="ticketTitle" placeholder="e.g., Wi-Fi Down in Hall A">
                
                <label for="aiProvider">AI Provider</label>
                <select id="aiProvider">
                    <option value="gemini">Gemini (Flash)</option>
                    <option value="openrouter">OpenRouter (GPT-4o-mini)</option>
                    <option value="groq">Groq (OSS-20b)</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="ticketDesc">Problem Description</label>
                <textarea id="ticketDesc" placeholder="Describe the issue in detail here..."></textarea>
                <button id="submitBtn">🚀 Submit & Run AI Analysis</button>
            </div>
        </div>

        <!-- Bottom Terminal Command Line -->
        <div class="cli-row">
            <span style="color: #8b949e;">$</span>
            <input type="text" id="cmdInput" placeholder="Terminal command (type 'help' or 'list')...">
        </div>
    </div>

    <script>
        const output = document.getElementById('output');
        const submitBtn = document.getElementById('submitBtn');
        const titleInput = document.getElementById('ticketTitle');
        const descInput = document.getElementById('ticketDesc');
        const providerSelect = document.getElementById('aiProvider');
        const cmdInput = document.getElementById('cmdInput');

        async function processSubmission(title, description, provider) {
            if (!title || !description) {
                output.innerText += "\\n❌ Error: Please provide both a title and description.\\n\\n";
                output.scrollTop = output.scrollHeight;
                return;
            }

            output.innerText += `\\n🚀 Creating ticket & analyzing with ${provider.toUpperCase()}...\\n`;
            output.scrollTop = output.scrollHeight;

            try {
                const res = await fetch('/api/ticket', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ title, description, provider })
                });
                const result = await res.json();
                output.innerText += result.output + "\\n\\n";
            } catch (err) {
                output.innerText += "❌ Execution failed.\\n\\n";
            }
            output.scrollTop = output.scrollHeight;
        }

        submitBtn.addEventListener('click', () => {
            processSubmission(titleInput.value.trim(), descInput.value.trim(), providerSelect.value);
        });

        cmdInput.addEventListener('keydown', async function(e) {
            if (e.key === 'Enter') {
                const cmd = cmdInput.value.trim();
                if (!cmd) return;
                
                output.innerText += `\\n$ ${cmd}\\n`;
                cmdInput.value = '';
                output.scrollTop = output.scrollHeight;

                if (cmd.toLowerCase() === 'help') {
                    output.innerText += "Commands:\\n  help - View help\\n  list - View tickets\\n  Or use the form above to submit issues easily!\\n\\n";
                    output.scrollTop = output.scrollHeight;
                    return;
                }

                if (cmd.toLowerCase() === 'list') {
                    try {
                        const res = await fetch('/tickets');
                        const data = await res.json();
                        output.innerText += JSON.stringify(data, null, 2) + "\\n\\n";
                    } catch (err) {
                        output.innerText += "Error fetching tickets.\\n\\n";
                    }
                    output.scrollTop = output.scrollHeight;
                    return;
                }

                try {
                    const res = await fetch('/run', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ command: cmd, provider: providerSelect.value })
                    });
                    const result = await res.json();
                    output.innerText += result.output + "\\n\\n";
                } catch (err) {
                    output.innerText += "Execution failed.\\n\\n";
                }
                output.scrollTop = output.scrollHeight;
            }
        });
    </script>
</body>
</html>"""

@app.get("/tickets")
def get_tickets():
    if not os.path.exists(FILE):
        return []
    try:
        with open(FILE, "r") as f:
            return json.load(f)
    except:
        return []

@app.post("/api/ticket")
def create_ticket_form(req: TicketRequest):
    tickets = []
    if os.path.exists(FILE):
        try:
            with open(FILE, "r") as f:
                tickets = json.load(f)
        except:
            tickets = []

    ticket_id = max([t["id"] for t in tickets], default=0) + 1
    tickets.append({"id": ticket_id, "title": req.title, "description": req.description})

    try:
        with open(FILE, "w") as f:
            json.dump(tickets, f, indent=4)
    except:
        return {"output": "❌ Error writing to tickets storage."}

    ai_suggestion = run_ai_analysis(req.description, req.provider)
    
    response_text = f"✅ Ticket #{ticket_id} Created Successfully!\n" \
                    f"Title: {req.title}\n" \
                    f"Description: {req.description}\n" \
                    f"--- AI Suggestions ({req.provider.capitalize()}) ---\n" \
                    f"{ai_suggestion}"
    return {"output": response_text}

@app.post("/run")
def run_command(req: CommandRequest):
    cmd = req.command.strip()
    if cmd.startswith("create "):
        parts = cmd[7:].split("|")
        if len(parts) < 2:
            return {"output": "❌ Error: Use format -> create Title | Description"}
        
        title = parts[0].strip()
        description = parts[1].strip()

        tickets = []
        if os.path.exists(FILE):
            try:
                with open(FILE, "r") as f:
                    tickets = json.load(f)
            except:
                tickets = []

        ticket_id = max([t["id"] for t in tickets], default=0) + 1
        tickets.append({"id": ticket_id, "title": title, "description": description})

        try:
            with open(FILE, "w") as f:
                json.dump(tickets, f, indent=4)
        except:
            return {"output": "❌ Error writing to tickets storage."}

        ai_suggestion = run_ai_analysis(description, req.provider)
        
        response_text = f"✅ Ticket #{ticket_id} Created Successfully!\n" \
                        f"Title: {title}\n" \
                        f"Description: {description}\n" \
                        f"--- AI Suggestions ({req.provider.capitalize()}) ---\n" \
                        f"{ai_suggestion}"
        return {"output": response_text}

    return {"output": f"❌ Command not recognized: {cmd}. Type 'help' for instructions."}