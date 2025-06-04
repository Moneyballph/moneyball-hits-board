import streamlit as st
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

def calculate_parlay_probability(p1, p2):
    return p1 * p2

# --- Session State ---
if 'players' not in st.session_state:
    st.session_state.players = []

# --- Title ---
st.image("moneyball_logo.png", width=160)
st.title("💰 Moneyball Phil: Daily Hit Probability Simulator")

# --- Player Stat Input ---
st.header("📥 Player Stat Input")
with st.form("player_input_form"):
    name = st.text_input("Player Name")
    season_avg = st.number_input("Season AVG", min_value=0.0, max_value=1.0, step=0.0001, format="%.4f")
    last7_avg = st.number_input("Last 7 Days AVG", min_value=0.0, max_value=1.0, step=0.0001, format="%.4f")
    split_avg = st.number_input("Home/Away or vs AL/NL AVG", min_value=0.0, max_value=1.0, step=0.0001, format="%.4f")
    handedness = st.selectbox("Starting Pitcher Handedness", ["RHP", "LHP"])
    pitcher_avg = st.number_input("Batter’s AVG vs Starting Pitcher", min_value=0.0, max_value=1.0, step=0.0001, format="%.4f")
    pitcher_ab = st.number_input("At-Bats vs Pitcher", min_value=0, step=1)
    odds = st.number_input("Sportsbook Odds (American)", step=1)

    weighted_avg = calculate_weighted_avg(season_avg, last7_avg, split_avg, pitcher_avg, pitcher_ab)
    st.markdown(f"**Weighted Batting Average:** {weighted_avg}")

    submit = st.form_submit_button("Simulate Player")

    if submit:
        true_hit_prob = binomial_hit_probability(weighted_avg)
        implied_prob = american_to_implied(odds)
        ev = (true_hit_prob - implied_prob) * 100
        zone = "Elite" if true_hit_prob > 0.8 else "Strong" if true_hit_prob > 0.7 else "Moderate" if true_hit_prob > 0.6 else "Bad"

        st.session_state.players.append({
            "name": f"{name} vs {handedness}",
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
    sorted_players = sorted(st.session_state.players, key=lambda x: x['prob'], reverse=True)
    st.table([
        {
            "Rank": i+1,
            "Player": p["name"],
            "True Hit Probability": f"{p['prob']}%",
            "Zone": p["zone"]
        } for i, p in enumerate(sorted_players)
    ])

# --- Parlay Builder ---
st.header("🧮 Parlay Builder")
st.caption("Select 2 players from the Top Hit Board to calculate parlay EV vs sportsbook odds.")

if len(st.session_state.players) >= 2:
    names = [p["name"] for p in st.session_state.players]
    p1_name = st.selectbox("Select Player 1", names, key="p1")
    p2_name = st.selectbox("Select Player 2", names, key="p2")
    parlay_odds = st.number_input("Enter Parlay Odds (American)", step=1, key="parlay_odds")

    if p1_name != p2_name:
        player1 = next(p for p in st.session_state.players if p['name'] == p1_name)
        player2 = next(p for p in st.session_state.players if p['name'] == p2_name)

        p1_prob = player1['prob'] / 100
        p2_prob = player2['prob'] / 100

        true_parlay_prob = calculate_parlay_probability(p1_prob, p2_prob)
        implied_parlay_prob = american_to_implied(parlay_odds)
        ev_parlay = (true_parlay_prob - implied_parlay_prob) * 100

        st.markdown(f"**True Parlay Probability:** {round(true_parlay_prob * 100, 1)}%")
        st.markdown(f"**Implied Probability:** {round(implied_parlay_prob * 100, 1)}%")
        st.markdown(f"**Expected Value (EV%):** {round(ev_parlay, 1)}%")

        if ev_parlay > 0:
            st.success("✅ This is a +EV Parlay!")
        else:
            st.error("❌ Negative EV Parlay")
    else:
        st.warning("Please select two different players.")
else:
    st.info("Add at least 2 players to use the Parlay Builder.")
