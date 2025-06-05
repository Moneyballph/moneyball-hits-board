
import streamlit as st
import math
import base64

# Set up custom background image
def set_background():
    with open("baseball_diamond_bg.png", "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode()
    bg_css = f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{encoded}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    </style>
    """
    st.markdown(bg_css, unsafe_allow_html=True)

set_background()

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
    return 1 - (1 - avg) ** ab

def american_to_implied(odds):
    if odds < 0:
        return abs(odds) / (abs(odds) + 100)
    else:
        return 100 / (odds + 100)

def calculate_parlay_probability(*probs):
    result = 1
    for p in probs:
        result *= p
    return result

def get_zone(prob):
    if prob > 0.8:
        return "Elite"
    elif prob > 0.7:
        return "Strong"
    elif prob > 0.6:
        return "Moderate"
    else:
        return "Bad"

# --- UI Setup ---
st.image("moneyball_logo.png", width=160)
st.title("💰 Moneyball Phil: Daily Hit Probability Simulator")

if 'players' not in st.session_state:
    st.session_state.players = []

# --- Player Input ---
st.header("📥 Player Stat Input")
with st.form("player_input_form"):
    name = st.text_input("Player Name")
    season_avg = st.number_input("Season AVG", 0.0, 1.0, step=0.0001, format="%0.4f")
    last7_avg = st.number_input("Last 7 Days AVG", 0.0, 1.0, step=0.0001, format="%0.4f")
    split_avg = st.number_input("Home/Away or vs AL/NL AVG", 0.0, 1.0, step=0.0001, format="%0.4f")
    pitcher_avg = st.number_input("Batter’s AVG vs Starting Pitcher", 0.0, 1.0, step=0.0001, format="%0.4f")
    pitcher_ab = st.number_input("At-Bats vs Pitcher", 0, step=1)
    odds = st.number_input("Sportsbook Odds (American)", step=1)

    weighted_avg = calculate_weighted_avg(season_avg, last7_avg, split_avg, pitcher_avg, pitcher_ab)
    st.markdown(f"**Weighted Batting Average:** `{weighted_avg:.4f}`")

    if st.form_submit_button("Simulate Player"):
        true_hit_prob = binomial_hit_probability(weighted_avg)
        implied_prob = american_to_implied(odds)
        ev = (true_hit_prob - implied_prob) * 100
        zone = get_zone(true_hit_prob)

        st.session_state.players.append({
            "name": name,
            "prob": round(true_hit_prob * 100, 1),
            "zone": zone,
            "ev": round(ev, 1),
            "odds": odds,
            "implied": round(implied_prob * 100, 1)
        })

# --- Top Hit Board ---
st.header("🔥 Top Hit Board")
if not st.session_state.players:
    st.info("No players simulated yet.")
else:
    sorted_players = sorted(st.session_state.players, key=lambda x: x["prob"], reverse=True)
    st.table([
        {
            "Rank": i + 1,
            "Player": p["name"],
            "True Hit Probability": f"{p['prob']}%",
            "Implied Probability": f"{p['implied']}%",
            "EV%": f"{p['ev']}%",
            "Zone": p["zone"]
        } for i, p in enumerate(sorted_players)
    ])

# --- Parlay Builder ---
st.header("🧮 Parlay Builder")
if len(st.session_state.players) >= 2:
    player_names = [p["name"] for p in st.session_state.players]
    selected = st.multiselect("Select 2 or 3 players", player_names, max_selections=3)

    if len(selected) >= 2:
        selected_probs = [p["prob"] / 100 for p in st.session_state.players if p["name"] in selected]
        parlay_odds = st.number_input("Enter Parlay Odds (American)", step=1)

        true_parlay_prob = calculate_parlay_probability(*selected_probs)
        implied_parlay_prob = american_to_implied(parlay_odds)
        ev_parlay = (true_parlay_prob - implied_parlay_prob) * 100
        parlay_zone = get_zone(true_parlay_prob)

        st.markdown(f"**True Parlay Probability:** `{true_parlay_prob * 100:.1f}%`")
        st.markdown(f"**Implied Probability:** `{implied_parlay_prob * 100:.1f}%`")
        st.markdown(f"**Expected Value (EV%):** `{ev_parlay:.1f}%`")
        st.markdown(f"**Parlay Zone:** `{parlay_zone}`")
        if ev_parlay > 0:
            st.success("✅ This is a +EV Parlay!")
        else:
            st.error("❌ Negative EV Parlay")
