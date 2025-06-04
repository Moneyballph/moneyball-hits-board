
import streamlit as st
from PIL import Image
import pandas as pd

# Set layout
st.set_page_config(layout="centered")

# Load and display logo
logo = Image.open("mbp_logo.png")
st.image(logo, width=180)

# Title
st.title("Moneyball Phil: Daily Hit Probability Simulator")

# Create session state for hit board
if "hit_board" not in st.session_state:
    st.session_state.hit_board = []

# Input fields (vertically stacked)
player_name = st.text_input("Player Name")
last7 = st.number_input("Last 7 Days AVG", format="%.3f", step=0.001)
vs_pitcher = st.number_input("AVG vs Pitcher", format="%.3f", step=0.001)
home_away = st.number_input("Home/Away AVG", format="%.3f", step=0.001)
vs_handedness = st.number_input("AVG vs Handedness", format="%.3f", step=0.001)
season_avg = st.number_input("Season AVG", format="%.3f", step=0.001)
odds = st.text_input("Sportsbook Odds (e.g., -145)")

# Automatically calculate weighted average
weighted_avg = round((last7 * 0.30 + vs_pitcher * 0.10 + home_away * 0.20 + vs_handedness * 0.10 + season_avg * 0.30), 3)

# Show weighted avg in its own box
st.markdown(f"### 📊 Weighted AVG: `{weighted_avg}`")

# Analyze player
if st.button("Analyze Player"):
    st.success(f"{player_name} analyzed and added to the Hit Board.")
    st.session_state.hit_board.append({
        "Player": player_name,
        "Weighted AVG": weighted_avg,
        "Odds": odds
    })

# Display Hit Board
if st.session_state.hit_board:
    st.markdown("---")
    st.subheader("📋 Live Hit Board")
    hit_board_df = pd.DataFrame(st.session_state.hit_board)
    st.dataframe(hit_board_df, use_container_width=True)
