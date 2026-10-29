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
    <title>Campus Ticket AI Terminal</title>
    <style>
        body { background-color: #0d1117; color: #58a6ff; font-family: 'Courier New', Courier, monospace; margin: 0; padding: 20px; }
        .container { max-width: 900px; margin: auto; background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
        h1 { color: #f0f6fc; font-size: 1.5rem; margin-top: 0; border-bottom: 1px solid #30363d; padding-bottom: 10px; }
        #output { height: 400px; overflow-y: auto; background: #010409; padding: 15px; border-radius: 6px; border: 1px solid #30363d; margin-bottom: 15px; white-space: pre-wrap; font-size: 14px; line-height: 1.4; color: #c9d1d9; }
        .input-row { display: flex; gap: 10px; align-items: center; }
        select, input { background: #0d1117; color: #c9d1d9; border: 1px solid #30363d; padding: 10px; border-radius: 6px; font-family: inherit; outline: none; }
        select { cursor: pointer; }
        input { flex-grow: 1; }
        input:focus, select:focus { border-color: #58a6ff; }
        .help-text { color: #8b949e; font-size: 0.85rem; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>⚡ Campus Ticket Web Terminal</h1>
        <div id="output">Welcome to the Campus Ticket AI Terminal!
Type commands below or click 'help' to see available options.

Available commands:
  help                             - Show command instructions
  create <title> | <description>   - Create a ticket and run AI analysis
  list                             - View saved tickets
</div>
        <div class="input-row">
            <select id="provider">
                <option value="gemini">Gemini</option>
                <option value="openrouter">OpenRouter</option>
                <option value="groq">Groq</option>
            </select>
            <input type="text" id="cmdInput" placeholder="Enter command (e.g., create Wi-Fi | Library network is dropping)..." autofocus>
        </div>
        <div class="help-text">Tip: Use format <b>create Title | Description</b> to submit tickets.</div>
    </div>

    <script>
        const output = document.getElementById('output');
        const cmdInput = document.getElementById('cmdInput');
        const providerSelect = document.getElementById('provider');

        cmdInput.addEventListener('keydown', async function(e) {
            if (e.key === 'Enter') {
                const cmd = cmdInput.value.trim();
                if (!cmd) return;
                
                output.innerText += "\\n$ " + cmd + "\\n";
                cmdInput.value = '';
                output.scrollTop = output.scrollHeight;

                if (cmd.toLowerCase() === 'help') {
                    output.innerText += "Commands:\\n  help - View help\\n  list - View tickets\\n  create <title> | <description> - Create ticket & analyze with AI\\n\\n";
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
                    output.innerText += "Processing via " + providerSelect.value + "...\\n";
                    output.scrollTop = output.scrollHeight;
                    
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