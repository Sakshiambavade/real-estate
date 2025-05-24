import streamlit as st
import json
import os
from dotenv import load_dotenv
from groq import Groq

# Load env
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

# Initialize Groq client
client = Groq(api_key=api_key)

# Load JSON data
with open("data.json", "r") as f:
    data = json.load(f)

sample_structure = json.dumps(data[:3], indent=2)

# Function to parse query using Groq AI
def analyze_query_with_ai(query):
    prompt = f"""
You are an AI real estate assistant. Given the data format below:

{sample_structure}

Convert the following natural language query into structured filters:

"{query}"

Return output ONLY in JSON like:
{{
  "bedrooms": 2,
  "city": "Pune",
  "type": "flat",
  "max_price": 6000000,
  "location": null
}}

Return null if a value is not available.
"""

    try:
        result = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "You convert user queries into structured filters for real estate search."},
                {"role": "user", "content": prompt}
            ]
        )
        response_text = result.choices[0].message.content
        filters = json.loads(response_text)
        return filters
    except Exception as e:
        st.error(f"AI parsing failed: {e}")
        return {}

# Filter listings using AI response
def filter_data(filters):
    results = []
    for item in data:
        if filters.get("bedrooms") and item["bedrooms"] != filters["bedrooms"]:
            continue
        if filters.get("city") and item["city"].lower() != filters["city"].lower():
            continue
        if filters.get("type") and item["type"].lower() != filters["type"].lower():
            continue
        if filters.get("location") and filters["location"].lower() not in item["location"].lower():
            continue
        if filters.get("max_price") and item["price"] > filters["max_price"]:
            continue
        results.append(item)
    return results

# Streamlit UI
st.set_page_config(page_title="AI Real Estate Search", page_icon="🏠")
st.title("🏠 AI-Powered Real Estate Search")
user_query = st.text_input("Ask: e.g., '2 BHK flat in Pune under 60 lakhs'")

if user_query:
    with st.spinner("Analyzing your query with Groq..."):
        filters = analyze_query_with_ai(user_query)
        st.write("🔎 Detected Filters:", filters)

        results = filter_data(filters)

        st.subheader("📄 Matching Results")
        if results:
            for res in results:
                st.markdown(f"""
                **{res['title']}**  
                📍 Location: {res['location']}, {res['city']}  
                🛏 Bedrooms: {res['bedrooms']} | 🛁 Bathrooms: {res['bathrooms']}  
                💰 Price: ₹{res['price']:,}
                ---
                """)
        else:
            st.warning("No matching listings found.")
