
import streamlit as st
from PIL import Image

# Load and display the logo
st.set_page_config(layout="wide")
logo = Image.open("mbp_logo.png")
st.image(logo, use_column_width=False, width=180)

st.title("Moneyball Phil: Daily Hit Tracker")

# Example input fields
player = st.text_input("Player Name")
avg = st.number_input("Season AVG", format="%.3f")
odds = st.text_input("Odds (e.g., -150)")
submit = st.button("Calculate")

if submit:
    st.success(f"Processing hit probability for {player}...")
    # Placeholder for backend logic
    st.info("Calculation result will go here.")
