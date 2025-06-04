
import streamlit as st
from PIL import Image

# Set layout
st.set_page_config(layout="wide")

# Load and display logo
logo = Image.open("mbp_logo.png")
st.image(logo, width=180)

# App title
st.title("Moneyball Phil: Daily Hit Probability Simulator")

# Input columns
col1, col2, col3 = st.columns(3)

with col1:
    last7 = st.number_input("Last 7 Days AVG", format="%.3f", step=0.001)
    vs_pitcher = st.number_input("AVG vs Pitcher", format="%.3f", step=0.001)

with col2:
    home_away = st.number_input("Home/Away AVG", format="%.3f", step=0.001)
    vs_handedness = st.number_input("AVG vs Handedness", format="%.3f", step=0.001)

with col3:
    season_avg = st.number_input("Season AVG", format="%.3f", step=0.001)
    odds = st.text_input("Sportsbook Odds (e.g., -145)")

# Calculate weighted average
if st.button("Calculate Weighted AVG"):
    weighted_avg = round((last7 * 0.30 + vs_pitcher * 0.10 + home_away * 0.20 + vs_handedness * 0.10 + season_avg * 0.30), 3)
    st.markdown("---")
    st.subheader(f"📊 Weighted Batting Average: `{weighted_avg}`")
    st.success("Now use this to calculate true hit probability or add to your hit tracker.")

