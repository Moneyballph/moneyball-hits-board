
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Moneyball Phil: Daily Hit Probability Simulator", layout="centered")

# Logo
st.image("mbp_logo.png", use_container_width=True)

st.title("Moneyball Phil: Daily Hit Probability Simulator")
st.markdown("---")

# Initialize session state for storing analyzed players
if "hit_board" not in st.session_state:
    st.session_state.hit_board = []

# Player input form
with st.form("player_form"):
    player_name = st.text_input("Player Name")
    avg_last7 = st.number_input("Last 7 Days AVG", format="%.3f")
    avg_pitcher = st.number_input("AVG vs Pitcher", format="%.3f")
    avg_homeaway = st.number_input("Home/Away AVG", format="%.3f")
    avg_handedness = st.number_input("AVG vs Handedness", format="%.3f")
    avg_season = st.number_input("Season AVG", format="%.3f")
    odds = st.text_input("Sportsbook Odds (e.g., -185 or +130)")

    submitted = st.form_submit_button("Analyze Player")

    if submitted and player_name:
        # Calculate Weighted AVG
        weighted_avg = round((avg_last7 * 0.30 + avg_pitcher * 0.10 + avg_homeaway * 0.15 +
                             avg_handedness * 0.15 + avg_season * 0.30), 3)

        # Convert sportsbook odds to implied probability
        try:
            american_odds = int(odds)
            if american_odds < 0:
                implied_prob = round(abs(american_odds) / (abs(american_odds) + 100), 4)
            else:
                implied_prob = round(100 / (american_odds + 100), 4)
        except:
            implied_prob = 0.0

        # Binomial 4-AB probability of at least 1 hit
        hit_prob = round(1 - (1 - weighted_avg)**4, 4)
        ev = round((hit_prob - implied_prob) * 100, 2)

        # Determine Hit Zone
        if hit_prob >= 0.80:
            zone = "Elite"
        elif hit_prob >= 0.70:
            zone = "Strong"
        elif hit_prob >= 0.60:
            zone = "Moderate"
        else:
            zone = "Bad"

        # Save to session state
        st.session_state.hit_board.append({
            "Player": player_name,
            "Weighted AVG": weighted_avg,
            "Hit %": hit_prob,
            "Implied %": implied_prob,
            "EV %": ev,
            "Zone": zone
        })

# Display Hit Board
if st.session_state.hit_board:
    df = pd.DataFrame(st.session_state.hit_board)
    st.subheader("📊 Live Hit Board")
    st.dataframe(df.reset_index(drop=True), use_container_width=True)
