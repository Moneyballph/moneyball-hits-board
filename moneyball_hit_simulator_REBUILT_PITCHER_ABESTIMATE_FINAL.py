
import streamlit as st
import pandas as pd
import base64

st.set_page_config(page_title="Moneyball Phil Hit Simulator", layout="centered")

def set_background(image_file):
    with open(image_file, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    css = f'''
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{data}");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
        background-position: center;
    }}
    </style>
    '''
    st.markdown(css, unsafe_allow_html=True)

set_background("background.png")
st.image("moneyball_logo.png", width=180)
st.title("💰 Moneyball Phil: Hit Probability Simulator")

st.header("📥 Player Stat Entry")
with st.form("player_input"):
    name = st.text_input("Player Name")
    season_avg = st.number_input("Season AVG", 0.0, 1.0, step=0.0001, format="%.4f")
    last7_avg = st.number_input("Last 7 Days AVG", 0.0, 1.0, step=0.0001, format="%.4f")
    split_avg = st.number_input("Split AVG (Home/Away)", 0.0, 1.0, step=0.0001, format="%.4f")
    hand_avg = st.number_input("AVG vs Handedness", 0.0, 1.0, step=0.0001, format="%.4f")
    pitcher_avg = st.number_input("AVG vs Pitcher", 0.0, 1.0, step=0.0001, format="%.4f")
    pitcher_era = st.number_input("Pitcher ERA", 0.0, 15.0, step=0.01)
    pitcher_whip = st.number_input("Pitcher WHIP", 0.0, 3.0, step=0.01)
    pitcher_k9 = st.number_input("Pitcher K/9", 0.0, 20.0, step=0.1)
    batting_order = st.selectbox("Batting Order Position", list(range(1, 10)))
    ab_vs_pitcher = st.number_input("At-Bats vs Pitcher", min_value=0, step=1)
    pitcher_hand = st.selectbox("Pitcher Handedness", ["Right", "Left"])
    batting_order = st.selectbox("Batting Order Position", list(range(1, 10)))
    odds = st.number_input("Sportsbook Odds (American)", step=1)
    submit = st.form_submit_button("Simulate Player")

if "players" not in st.session_state:
    st.session_state.players = []

def calculate_weighted_avg(season, last7, split, hand, pitcher):
    return round(0.2 * season + 0.3 * last7 + 0.2 * split + 0.2 * hand + 0.1 * pitcher, 4)

def binomial_hit_probability(avg, ab=4):
    return round(1 - (1 - avg)**ab, 4)

def american_to_implied(odds):
    return round(abs(odds) / (abs(odds) + 100), 4) if odds < 0 else round(100 / (odds + 100), 4)

def classify_zone(prob):
    if prob >= 0.8:
        return "🟩 Elite"
    elif prob >= 0.7:
        return "🟨 Strong"
    elif prob >= 0.6:
        return "🟧 Moderate"
    else:
        return "🟥 Risky"

if submit:
    weighted_avg = calculate_weighted_avg(season_avg, last7_avg, split_avg, hand_avg, pitcher_avg)
    st.markdown(f"**Weighted AVG:** `{weighted_avg}`")
    
weighted_avg = calculate_weighted_avg(season_avg, last7_avg, split_avg, hand_avg, pitcher_avg)

# Apply Pitcher Difficulty Modifier
adjustment = 0
if pitcher_whip >= 1.40 or pitcher_era >= 5.00:
    adjustment = 0.020
    tier = "🟢 Easy Pitcher"
elif pitcher_whip < 1.10 or pitcher_era < 3.50:
    adjustment = -0.020
    tier = "🔴 Tough Pitcher"
else:
    adjustment = 0.000
    tier = "🟨 Average Pitcher"

adj_weighted_avg = round(weighted_avg + adjustment, 4)
st.markdown(f"**Weighted AVG (Before Adjustment):** `{weighted_avg}`")
st.markdown(f"**Pitcher Difficulty Tier:** {tier} (`{adjustment:+.3f}`)")
st.markdown(f"**Adjusted Weighted AVG:** `{adj_weighted_avg}`")


# Estimate ABs based on batting order
ab_lookup = {1: 4.6, 2: 4.5, 3: 4.4, 4: 4.3, 5: 4.2, 6: 4.0, 7: 3.8, 8: 3.6, 9: 3.4}
est_ab = ab_lookup.get(batting_order, 4.0)
st.markdown(f"**Estimated At-Bats:** {est_ab} (based on batting {batting_order}th)")

true_prob = binomial_hit_probability(adj_weighted_avg, ab=round(est_ab))


implied_prob = american_to_implied(odds)
ev = round((true_prob - implied_prob) * 100, 1)
zone = classify_zone(true_prob)

    st.session_state.players.append({
        "name": name,
        "true_prob": true_prob,
        "implied_prob": implied_prob,
        "ev": ev,
        "zone": zone
    })

st.header("🔥 Top Hit Board")
if st.session_state.players:
    df = pd.DataFrame(st.session_state.players)
    df.insert(0, "Rank", range(1, len(df) + 1))
    df["True Prob %"] = (df["true_prob"] * 100).round(1)
    df["Implied %"] = (df["implied_prob"] * 100).round(1)
    df["EV %"] = df["ev"]
    st.dataframe(df[["Rank", "name", "True Prob %", "Implied %", "EV %", "zone"]], use_container_width=True)
else:
    st.info("Add players above to populate the Top Hit Board.")

st.header("🧮 Parlay Builder")
if len(st.session_state.players) >= 2:
    names = [p["name"] for p in st.session_state.players]
    selected = st.multiselect("Select 2 or 3 Players", names)
    if len(selected) in [2, 3]:
        probs = [p["true_prob"] for p in st.session_state.players if p["name"] in selected]
        implieds = [p["implied_prob"] for p in st.session_state.players if p["name"] in selected]
        parlay_true = round(pd.Series(probs).prod(), 4)

        st.markdown("### 📉 Sportsbook Parlay Odds Input")
        parlay_odds = st.number_input("Enter Combined Parlay Odds (American)", step=1, key="parlay_odds")
        implied_parlay_prob = american_to_implied(parlay_odds)
        parlay_ev = round((parlay_true - implied_parlay_prob) * 100, 1)

        if parlay_true >= 0.75:
            pzone = "🟩 Elite Parlay"
        elif parlay_true >= 0.60:
            pzone = "🟨 Strong Parlay"
        elif parlay_true >= 0.45:
            pzone = "🟧 Moderate Parlay"
        else:
            pzone = "🟥 Risky Parlay"

        st.markdown(f"**True Parlay Probability:** {parlay_true:.2%}")
        st.markdown(f"**Implied Parlay Probability:** {implied_parlay_prob:.2%}")
        st.markdown(f"**Parlay EV %:** {parlay_ev:+.1f}%")
        st.markdown(f"**Parlay Zone:** {pzone}")
    elif len(selected) > 3:
        st.warning("Please select only 2 or 3 players.")
else:
    st.info("Add at least 2 players to use the Parlay Builder.")
