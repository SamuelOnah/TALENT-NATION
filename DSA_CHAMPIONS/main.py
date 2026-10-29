import os
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import json
from pathlib import Path

# AI SDKs
from google import genai
from openai import OpenAI
from groq import Groq

app = FastAPI(title="Campus Ticket AI Playground")

# Data file for persistent tickets
TICKETS_FILE = Path("tickets.json")

def load_tickets():
    if TICKETS_FILE.exists():
        try:
            with open(TICKETS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_tickets(tickets):
    with open(TICKETS_FILE, "w") as f:
        json.dump(tickets, f, indent=2)

def run_ai_analysis(description: str, provider: str) -> str:
    prompt = f"Analyze this campus tech problem and suggest 3-4 concise ways to fix or investigate it. Wrap key terms or emphasis in double asterisks like **this**: {description}"
    try:
        if provider == "gemini":
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                return "❌ Error: GEMINI_API_KEY is missing in your environment variables."
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt,
            )
            return response.text
            
        elif provider == "openrouter":
            api_key = os.environ.get("OPENROUTER_API_KEY")
            if not api_key:
                return "❌ Error: OPENROUTER_API_KEY is missing in your environment variables."
            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=api_key
            )
            response = client.chat.completions.create(
                model="openai/gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
            
        elif provider == "groq":
            api_key = os.environ.get("GROQ_API_KEY")
            if not api_key:
                return "❌ Error: GROQ_API_KEY is missing in your environment variables."
            client = Groq(api_key=api_key)
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        else:
            return "❌ Unknown AI provider selected."
    except Exception as e:
        return f"❌ Error connecting to {provider}: {str(e)}"

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Campus Ticket AI Playground</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;700&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <style>
            body { font-family: 'Inter', sans-serif; background-color: #090d16; color: #e2e8f0; }
            .code-font { font-family: 'Fira Code', monospace; }
            .glass-panel { background: rgba(17, 24, 39, 0.75); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.1); }
            .glow-cyan { box-shadow: 0 0 25px rgba(6, 182, 212, 0.15); }
            .glow-purple { box-shadow: 0 0 25px rgba(168, 85, 247, 0.15); }
            .custom-scrollbar::-webkit-scrollbar { width: 6px; }
            .custom-scrollbar::-webkit-scrollbar-track { background: rgba(15, 23, 42, 0.6); }
            .custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(51, 65, 85, 0.8); border-radius: 3px; }
        </style>
    </head>
    <body class="min-h-screen flex flex-col items-center justify-between p-4 sm:p-6">

        <!-- Top Header -->
        <header class="w-full max-w-4xl text-center my-6">
            <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-950/60 border border-cyan-500/30 text-cyan-400 text-xs font-medium tracking-wide mb-3 uppercase">
                <span class="w-2 h-2 rounded-full bg-cyan-400 animate-pulse"></span> Multi-AI Triage Engine Active
            </div>
            <h1 class="text-3xl sm:text-4xl font-extrabold tracking-tight text-white mb-2">
                Campus Ticket <span class="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-indigo-400">AI Playground</span>
            </h1>
            <p class="text-slate-400 text-sm max-w-lg mx-auto">
                Submit IT support issues and harness real-time multi-model intelligence to resolve campus requests instantly.
            </p>
        </header>

        <!-- Main Workspace -->
        <main class="w-full max-w-4xl grid grid-cols-1 md:grid-cols-3 gap-6 flex-grow mb-6">
            
            <!-- Left Column: Form Control Panel -->
            <section class="glass-panel rounded-2xl p-5 shadow-xl glow-cyan flex flex-col justify-between">
                <div>
                    <h2 class="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                        <svg class="w-5 h-5 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v3m0 0v3m0-3h3m-3 0H9m12 0a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                        New Ticket
                    </h2>
                    
                    <form id="ticketForm" class="space-y-4">
                        <div>
                            <label class="block text-xs font-medium text-slate-300 uppercase tracking-wider mb-1">Issue Title</label>
                            <input type="text" id="title" required placeholder="e.g., Slow Wi-Fi in Library" 
                                class="w-full bg-slate-900/80 border border-slate-700 rounded-xl px-3.5 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition">
                        </div>

                        <div>
                            <label class="block text-xs font-medium text-slate-300 uppercase tracking-wider mb-1">Description</label>
                            <textarea id="description" rows="3" required placeholder="Describe the problem in detail..." 
                                class="w-full bg-slate-900/80 border border-slate-700 rounded-xl px-3.5 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition"></textarea>
                        </div>

                        <div>
                            <label class="block text-xs font-medium text-slate-300 uppercase tracking-wider mb-1">Select AI Engine</label>
                            <select id="provider" class="w-full bg-slate-900/80 border border-slate-700 rounded-xl px-3.5 py-2.5 text-sm text-white focus:outline-none focus:border-cyan-500 transition">
                                <option value="gemini">Google Gemini (Flash)</option>
                                <option value="openrouter">OpenRouter (GPT-4o Mini)</option>
                                <option value="groq">Groq (Llama 3.3)</option>
                            </select>
                        </div>

                        <button type="submit" id="submitBtn" class="w-full bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-semibold py-2.5 px-4 rounded-xl shadow-lg shadow-cyan-500/20 transition-all duration-200 text-sm flex items-center justify-center gap-2">
                            <span>Analyze Ticket</span>
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
                        </button>
                    </form>
                </div>

                <div class="mt-6 pt-4 border-t border-slate-800/80 text-xs text-slate-500 text-center">
                    Render Cloud Environment • Ready
                </div>
            </section>

            <!-- Right Column: Interactive Terminal Output View -->
            <section class="glass-panel rounded-2xl p-5 shadow-xl glow-purple md:col-span-2 flex flex-col">
                <div class="flex items-center justify-between pb-3 border-b border-slate-800 mb-4">
                    <div class="flex items-center gap-2">
                        <div class="flex gap-1.5">
                            <span class="w-3 h-3 rounded-full bg-rose-500/80 inline-block"></span>
                            <span class="w-3 h-3 rounded-full bg-amber-500/80 inline-block"></span>
                            <span class="w-3 h-3 rounded-full bg-emerald-500/80 inline-block"></span>
                        </div>
                        <span class="code-font text-xs text-slate-400 ml-2">terminal-output://live-stream</span>
                    </div>
                    <button onclick="clearTerminal()" class="text-xs text-slate-400 hover:text-white transition px-2 py-1 rounded bg-slate-800/60 hover:bg-slate-700">Clear Feed</button>
                </div>

                <div id="terminalOutput" class="code-font text-xs bg-slate-950/80 border border-slate-800/80 rounded-xl p-4 flex-grow overflow-y-auto max-h-[420px] custom-scrollbar space-y-4 text-slate-300">
                    <div class="text-cyan-400">✨ System online. Waiting for ticket submission...</div>
                </div>
            </section>

        </main>

        <!-- Footer -->
        <footer class="text-xs text-slate-500 text-center py-2">
            Campus IT Helpdesk AI Playground &bull; Powered by FastAPI & Render
        </footer>

        <!-- Script handling API submission and formatting **bold** text -->
        <script>
            function formatMarkdown(text) {
                if (!text) return '';
                // Escape HTML to prevent injection, then format **text** to <strong>
                const escaped = text
                    .replace(/&/g, "&amp;")
                    .replace(/</g, "&lt;")
                    .replace(/>/g, "&gt;");
                
                // Convert **text** at beginning/end or anywhere to <strong>text</strong>
                return escaped.replace(/\\*\\*(.*?)\\*\\*/g, '<strong class="text-cyan-300 font-semibold">$1</strong>');
            }

            const terminal = document.getElementById('terminalOutput');

            function appendTerminal(htmlContent) {
                const div = document.createElement('div');
                div.innerHTML = htmlContent;
                terminal.appendChild(div);
                terminal.scrollTop = terminal.scrollHeight;
            }

            function clearTerminal() {
                terminal.innerHTML = '<div class="text-slate-500">Terminal cleared.</div>';
            }

            document.getElementById('ticketForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const title = document.getElementById('title').value;
                const description = document.getElementById('description').value;
                const provider = document.getElementById('provider').value;
                const btn = document.getElementById('submitBtn');

                btn.disabled = true;
                btn.innerHTML = `<svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg> Analyzing with ${provider.toUpperCase()}...`;

                appendTerminal(`<div><span class="text-slate-500">[$]</span> <span class="text-indigo-400">Creating ticket & analyzing with ${provider.toUpperCase()}...</span></div>`);

                try {
                    const response = await fetch('/api/tickets', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                        body: new URLSearchParams({ title, description, provider })
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok) {
                        const formattedAnalysis = formatMarkdown(data.analysis);
                        appendTerminal(`
                            <div class="bg-slate-900/90 border border-slate-800 rounded-lg p-3 space-y-2">
                                <div class="text-emerald-400 font-bold">✅ Ticket #${data.id} Created Successfully!</div>
                                <div class="text-white"><span class="text-slate-400">Title:</span> ${data.title}</div>
                                <div class="text-slate-300 border-t border-slate-800 pt-2 mt-1">
                                    <div class="text-cyan-400 font-semibold mb-1">--- AI Suggestions (${provider}) ---</div>
                                    <div class="leading-relaxed">${formattedAnalysis}</div>
                                </div>
                            </div>
                        `);
                    } else {
                        appendTerminal(`<div class="text-rose-400">❌ Error: ${data.detail || 'Failed to process ticket.'}</div>`);
                    }
                } catch (err) {
                    appendTerminal(`<div class="text-rose-400">❌ Network Error: ${err.message}</div>`);
                } finally {
                    btn.disabled = false;
                    btn.innerHTML = `<span>Analyze Ticket</span><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>`;
                }
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/api/tickets")
async def create_ticket(title: str = Form(...), description: str = Form(...), provider: str = Form(...)):
    tickets = load_tickets()
    new_id = len(tickets) + 1
    
    # Run the selected AI provider
    analysis = run_ai_analysis(description, provider)
    
    ticket_data = {
        "id": new_id,
        "title": title,
        "description": description,
        "provider": provider,
        "analysis": analysis
    }
    
    tickets.append(ticket_data)
    save_tickets(tickets)
    
    return ticket_data

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)