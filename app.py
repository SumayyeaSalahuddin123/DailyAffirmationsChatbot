import streamlit as st
import google.generativeai as genai
from datetime import datetime, timedelta
import json
import os

# Configure the app
st.set_page_config(page_title="Daily Affirmations", page_icon="🌞")

# Initialize Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

# System prompt for the AI
AFFIRMATION_PROMPT = """
You are a compassionate, uplifting affirmation assistant. Your role is to provide personalized daily affirmations based on how the user is feeling today.
Guidelines:
1. Always respond with kindness and empathy
2. Keep affirmations positive, present-tense, and personal (use "I" or "You")
3. Make them specific to the user's current emotional state
4. Provide 3 short affirmations (1 sentence each) that are easy to remember
5. Format the response clearly with each affirmation on a new line with a 🌟 emoji
Example for someone feeling anxious:
🌟 I am safe and in control of my breathing
🌟 My challenges help me grow stronger each day
🌟 I release worries and embrace peace in this moment
Now respond to the following user input:
"""

# File to store affirmation history
AFFIRMATION_HISTORY_FILE = "affirmation_history.json"

def load_affirmation_history():
    """Load affirmation history from file"""
    try:
        if os.path.exists(AFFIRMATION_HISTORY_FILE):
            with open(AFFIRMATION_HISTORY_FILE, 'r') as f:
                return json.load(f)
    except Exception:
        pass
    return {}

def save_affirmation_history(history):
    """Save affirmation history to file"""
    with open(AFFIRMATION_HISTORY_FILE, 'w') as f:
        json.dump(history, f)

def get_week_dates():
    """Get dates for the current week (Monday to Sunday)"""
    today = datetime.now()
    start_of_week = today - timedelta(days=today.weekday())  # Monday
    return [start_of_week + timedelta(days=i) for i in range(7)]

def generate_affirmation(user_feeling):
    """Generate affirmations using Gemini"""
    try:
        response = model.generate_content(AFFIRMATION_PROMPT + user_feeling)
        return response.text
    except Exception as e:
        st.error(f"Error generating affirmation: {e}")
        return None

def main():
    st.title("🌞 Daily Affirmations Chatbot")
    st.markdown("Share how you're feeling today and receive personalized affirmations!")
    
    # Initialize session state
    if 'affirmation_history' not in st.session_state:
        st.session_state.affirmation_history = load_affirmation_history()
    
    # User input
    user_feeling = st.text_input("How are you feeling today?", 
                               placeholder="E.g. anxious, excited, tired, hopeful...")
    
    if st.button("Get Affirmations"):
        if user_feeling.strip():
            with st.spinner("Generating your personalized affirmations..."):
                affirmations = generate_affirmation(user_feeling)
                
                if affirmations:
                    # Store the affirmation with today's date
                    today = datetime.now().strftime("%Y-%m-%d")
                    st.session_state.affirmation_history[today] = {
                        'feeling': user_feeling,
                        'affirmations': affirmations,
                        'date': today
                    }
                    save_affirmation_history(st.session_state.affirmation_history)
                    
                    st.success("Here are your affirmations for today:")
                    st.markdown(affirmations)
        else:
            st.warning("Please share how you're feeling to get affirmations.")
    
    # Display weekly log
    st.divider()
    st.subheader("📅 Your Affirmation Log This Week")
    
    week_dates = get_week_dates()
    has_history = False
    
    for date in week_dates:
        date_str = date.strftime("%Y-%m-%d")
        day_name = date.strftime("%A")
        
        if date_str in st.session_state.affirmation_history:
            has_history = True
            entry = st.session_state.affirmation_history[date_str]
            
            with st.expander(f"{day_name}, {date_str}: {entry['feeling']}"):
                st.markdown(entry['affirmations'])
    
    if not has_history:
        st.info("Your weekly log will appear here after you receive affirmations.")

if __name__ == "__main__":
    main()
