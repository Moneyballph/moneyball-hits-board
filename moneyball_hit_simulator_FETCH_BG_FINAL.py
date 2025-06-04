
import streamlit as st
import requests
import pandas as pd
import math

# --- Helper Functions ---
def calculate_weighted_avg(season, last7, split, pitcher_avg=None, pitcher_ab=0):
    pitcher_weight = 0.3 if pitcher_ab >= 7 else 0.1 if pitcher_ab > 0 else 0
    season_weight = 0.4
    recent_weight = 0.3
    split_weight = 0.3
    total_weight = season_weight + recent_weight + split_weight + pitcher_weight
    weighted_sum = (
        season * season_weight +
        last7 * recent_weight +
        split * split_weight +
        (pitcher_avg * pitcher_weight if pitcher_avg is not None else 0)
    )
    return weighted_sum / total_weight

def binomial_hit_probability(avg, ab=4):
    prob_no_hit = (1 - avg) ** ab
    return 1 - prob_no_hit

def american_to_implied(odds):
    if odds < 0:
        return abs(odds) / (abs(odds) + 100)
    else:
        return 100 / (odds + 100)

def calculate_parlay_probability(prob_list):
    result = 1
    for p in prob_list:
        result *= p
    return result

def fetch_mlb_stats(player_name):
    # Simulate MLB StatsAPI fetch for example purposes (fake data here)
    # Replace this section with actual API call and parsing logic if available
    fake_data = {
        "season_avg": 0.287,
        "last7_avg": 0.320,
        "split_avg": 0.298
    }
    return fake_data

# --- Background and Logo ---
st.markdown(
    f"<style>body {{background-image: url('background.png'); background-size: cover;}}</style>",
    unsafe_allow_html=True
)
st.image("moneyball_logo.png", width=160)
st.title("💰 Moneyball Phil: Daily Hit Probability Simulator")

# --- Session State ---
if 'players' not in st.session_state:
    st.session_state.players = []

# --- Player Input ---
st.header("📥 Player Stat Input")
with st.form("player_input_form"):
    name = st.text_input("Player Name")
    fetch = st.form_submit_button("Fetch Stats")

    season_avg = st.number_input("Season AVG", min_value=0.0, max_value=1.0, step=0.0001, format="%.4f")
    last7_avg = st.number_input("Last 7 Days AVG", min_value=0.0, max_value=1.0, step=0.0001, format="%.4f")
    split_avg = st.number_input("Home/Away or vs AL/NL AVG", min_value=0.0, max_value=1.0, step=0.0001, format="%.4f")
    pitcher_avg = st.number_input("Batter’s AVG vs Starting Pitcher", min_value=0.0, max_value=1.0, step=0.0001, format="%.4f")
    pitcher_ab = st.number_input("At-Bats vs Pitcher", min_value=0, step=1)
    odds = st.number_input("Sportsbook Odds (American)", step=1)

    if fetch and name:
        stats = fetch_mlb_stats(name)
        season_avg = stats['season_avg']
        last7_avg = stats['last7_avg']
        split_avg = stats['split_avg']
        st.experimental_rerun()

    weighted_avg = calculate_weighted_avg(season_avg, last7_avg, split_avg, pitcher_avg, pitcher_ab)
    st.markdown(f"**Weighted Batting Average:** `{round(weighted_avg, 4)}`")

    submit = st.form_submit_button("Simulate Player")
    if submit:
        true_hit_prob = binomial_hit_probability(weighted_avg)
        implied_prob = american_to_implied(odds)
        ev = (true_hit_prob - implied_prob) * 100
        zone = "Elite" if true_hit_prob > 0.8 else "Strong" if true_hit_prob > 0.7 else "Moderate" if true_hit_prob > 0.6 else "Bad"
        st.session_state.players.append({
            "name": name,
            "prob": round(true_hit_prob * 100, 1),
            "implied": round(implied_prob * 100, 1),
            "ev": round(ev, 1),
            "zone": zone
        })

# --- Top Hit Board ---
st.header("🔥 Top Hit Board")
if not st.session_state.players:
    st.info("No players simulated yet.")
else:
    sorted_players = sorted(st.session_state.players, key=lambda x: x['prob'], reverse=True)
    st.table([
        {
            "Rank": i+1,
            "Player": p["name"],
            "True Hit Probability": f"{p['prob']}%",
            "Implied Probability": f"{p['implied']}%",
            "EV%": f"{p['ev']}%",
            "Zone": p["zone"]
        } for i, p in enumerate(sorted_players)
    ])

# --- Parlay Builder (up to 3 legs) ---
st.header("🧮 Parlay Builder")
if len(st.session_state.players) >= 2:
    names = [p["name"] for p in st.session_state.players]
    selections = st.multiselect("Select 2 or 3 Players", names, max_selections=3)
    if len(selections) >= 2:
        selected_probs = [p["prob"]/100 for p in st.session_state.players if p["name"] in selections]
        parlay_odds = st.number_input("Enter Parlay Odds (American)", step=1, key="parlay_odds")
        true_parlay_prob = calculate_parlay_probability(selected_probs)
        implied_parlay_prob = american_to_implied(parlay_odds)
        ev_parlay = (true_parlay_prob - implied_parlay_prob) * 100
        st.markdown(f"**True Parlay Probability:** {round(true_parlay_prob * 100, 1)}%")
        st.markdown(f"**Implied Probability:** {round(implied_parlay_prob * 100, 1)}%")
        st.markdown(f"**Expected Value (EV%):** {round(ev_parlay, 1)}%")
        if ev_parlay > 0:
            st.success("✅ This is a +EV Parlay!")
        else:
            st.error("❌ Negative EV Parlay")
