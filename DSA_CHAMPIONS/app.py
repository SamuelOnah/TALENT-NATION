import json
import os
import time
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI  
from google import genai
from groq import Groq

load_dotenv()

FILE = "tickets.json"

st.set_page_config(page_title="Campus Ticket AI Analyzer", page_icon="🎫", layout="centered")

st.title("🎫 Campus Ticket AI Analyzer")
st.write("Submit a campus tech issue and get instant AI-powered troubleshooting suggestions.")

st.sidebar.header("AI Configuration")
provider_choice = st.sidebar.selectbox(
    "Select AI Provider",
    options=["Gemini", "OpenRouter", "Groq"]
)
provider = provider_choice.lower()

with st.form("ticket_form"):
    title = st.text_input("Ticket Title", placeholder="e.g., Slow Wi-Fi in Library")
    description = st.text_area("Ticket Description", placeholder="Describe the issue in detail...")
    submitted = st.form_submit_button("Create Ticket & Get AI Analysis")

if submitted:
    if not title or not description:
        st.error("Please fill in both the title and description.")
    else:
      
        tickets = []
        if os.path.exists(FILE):
            try:
                with open(FILE, "r") as f:
                    tickets = json.load(f)
            except (json.JSONDecodeError, OSError):
                tickets = []

        ticket_id = max([t["id"] for t in tickets], default=0) + 1
        new_ticket = {"id": ticket_id, "title": title, "description": description}
        tickets.append(new_ticket)

        try:
            with open(FILE, "w") as f:
                json.dump(tickets, f, indent=4)
            st.success(f"Ticket #{ticket_id} created successfully!")
        except OSError:
            st.error("Error saving ticket to file.")

   
        st.write(f"---")
        st.info(f"Analyzing ticket using **{provider_choice}**...")
        
        prompt = f"Analyze this campus tech problem and suggest 3-4 concise ways to fix or investigate it: {description}"
        
        try:
            ai_suggestion = ""
            if provider == "gemini":
                client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                )
                ai_suggestion = response.text
                
            elif provider == "openrouter":
                client = OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=os.environ.get("OPENROUTER_API_KEY")
                )
                response = client.chat.completions.create(
                    model="openai/gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}]
                )
                ai_suggestion = response.choices[0].message.content
                
            elif provider == "groq":
                client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
                response = client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=[{"role": "user", "content": prompt}]
                )
                ai_suggestion = response.choices[0].message.content

            st.subheader("💡 AI Troubleshooting Suggestions")
            st.markdown(ai_suggestion)
            
        except Exception as e:
            st.error(f"Could not fetch AI suggestions from {provider_choice}. Error: {e}")