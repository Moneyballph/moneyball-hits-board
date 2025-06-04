
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Moneyball Phil: Daily Hit Probability Simulator", layout="wide")

# Load logo
st.image("mbp_logo.png", use_container_width=False, width=150)

st.title("Moneyball Phil: Daily Hit Probability Simulator")

# Initialize session state
if "player_data" not in st.session_state:
    st.session_state.player_data = []

# Form inputs
with st.form("player_form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        player_name = st.text_input("Player Name")
        last7 = st.number_input("Last 7 Days AVG", min_value=0.0, max_value=1.0, step=0.001)
        vs_pitcher = st.number_input("AVG vs Pitcher", min_value=0.0, max_value=1.0, step=0.001)
    with col2:
        home_away = st.number_input("Home/Away AVG", min_value=0.0, max_value=1.0, step=0.001)
        handedness = st.number_input("AVG vs Handedness", min_value=0.0, max_value=1.0, step=0.001)
        season_avg = st.number_input("Season AVG", min_value=0.0, max_value=1.0, step=0.001)
    with col3:
        odds = st.number_input("Sportsbook Odds (American)", step=1)
        submitted = st.form_submit_button("Analyze Player")

# Process data
def calculate_implied_probability(odds):
    return round(abs(odds) / (abs(odds) + 100), 3) if odds < 0 else round(100 / (odds + 100), 3)

def calculate_weighted_avg(last7, vs_pitcher, home_away, handedness, season_avg):
    weights = [0.25, 0.2, 0.2, 0.15, 0.2]
    return round(sum([
        last7 * weights[0],
        vs_pitcher * weights[1],
        home_away * weights[2],
        handedness * weights[3],
        season_avg * weights[4]
    ]), 3)

def hit_zone(prob):
    if prob >= 0.8:
        return "Elite"
    elif prob >= 0.7:
        return "Strong"
    elif prob >= 0.6:
        return "Moderate"
    else:
        return "Bad"

if submitted and player_name:
    weighted = calculate_weighted_avg(last7, vs_pitcher, home_away, handedness, season_avg)
    true_prob = 1 - (1 - weighted) ** 4
    implied_prob = calculate_implied_probability(odds)
    ev = round((true_prob - implied_prob) * 100, 1)
    zone = hit_zone(true_prob)
    st.session_state.player_data.append({
        "Player": player_name,
        "Last 7": last7,
        "Vs Pitcher": vs_pitcher,
        "Home/Away": home_away,
        "Vs Handedness": handedness,
        "Season AVG": season_avg,
        "Weighted AVG": weighted,
        "True Hit %": round(true_prob, 3),
        "Implied %": implied_prob,
        "EV %": ev,
        "Hit Zone": zone
    })

# Display hit board
if st.session_state.player_data:
    df = pd.DataFrame(st.session_state.player_data)
    st.subheader("📊 Live Hit Board")
    st.dataframe(df, use_container_width=True)
