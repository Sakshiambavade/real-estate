import streamlit as st
import json
import os
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Load JSON data
with open("data.json", "r") as f:
    data = json.load(f)

# Sample to show model structure
sample_structure = json.dumps(data[:3], indent=2)

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)

# Analyze user query using Groq AI
def analyze_query_with_ai(query):
    prompt = f"""
You are an intelligent assistant helping to search real estate listings.

Here is a sample of the data:
{sample_structure}

Based on the user query below:
"{query}"

Extract meaningful filters using this JSON structure:
{{
  "bedrooms": int or null,
  "city": string or null,
  "type": string or null,
  "max_price": int or null,
  "location": string or null
}}

Respond ONLY with valid JSON and nothing else.
    """
    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "You're a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        content = response.choices[0].message.content.strip()
        parsed = json.loads(content)
        return parsed
    except Exception as e:
        st.error(f"AI parsing failed: {e}")
        return {}

# Filter listings based on AI output
def filter_data(filters):
    results = []
    for item in data:
        if filters.get("bedrooms") is not None and item.get("bedrooms") != filters["bedrooms"]:
            continue
        if filters.get("city") and item.get("city", "").lower() != filters["city"].lower():
            continue
        if filters.get("type") and item.get("type", "").lower() != filters["type"].lower():
            continue
        if filters.get("location") and filters["location"].lower() not in item.get("location", "").lower():
            continue
        if filters.get("max_price") is not None and item.get("price", 0) > filters["max_price"]:
            continue
        results.append(item)
    return results

# Streamlit UI
st.title("🏡 AI-Powered Real Estate Search")

user_query = st.text_input("Ask a question like: '2 BHK flat in Pune under 50 lakhs'")

if user_query:
    with st.spinner("Analyzing with AI..."):
        filters = analyze_query_with_ai(user_query)
        st.write("🔍 Detected Filters:")
        st.json(filters)

        results = filter_data(filters)

        st.subheader("📋 Matching Listings")
        if results:
            for res in results:
                st.markdown(f"""
                **{res.get('title', 'No Title')}**  
                📍 Location: {res.get('location', 'N/A')}, {res.get('city', 'N/A')}  
                🛏 Bedrooms: {res.get('bedrooms', 'N/A')} | 🛁 Bathrooms: {res.get('bathrooms', 'N/A')}  
                💰 Price: ₹{res.get('price', 'N/A'):,}
                ---
                """)
        else:
            st.warning("No matching listings found.")
