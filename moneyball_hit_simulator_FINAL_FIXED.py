
import streamlit as st
import pandas as pd
import base64

# Set page config
st.set_page_config(layout="wide", page_title="Moneyball Phil")

# Load logo
st.image("moneyball_logo.png", width=160)

# Set custom background
def set_background(image_file):
    with open(image_file, "rb") as f:
        data = f.read()
    encoded = base64.b64encode(data).decode()
    page_bg_img = f'''
    <style>
    .stApp {{
      background-image: url("data:image/png;base64,{encoded}");
      background-size: cover;
      background-position: center;
    }}
    </style>
    '''
    st.markdown(page_bg_img, unsafe_allow_html=True)

set_background("baseball_diamond_bg.png")

st.title("💰 Moneyball Phil: Daily Hit Probability Simulator")

# Input section
st.subheader("🔢 Player Stats Input")
col1, col2, col3 = st.columns(3)

with col1:
    player_name = st.text_input("Player Name")
    season_avg = st.number_input("Season AVG", format="%.4f")
    last7_avg = st.number_input("Last 7 Days AVG", format="%.4f")
    vs_team_avg = st.number_input("AVG vs Opponent Team", format="%.4f")

with col2:
    pitcher_hand = st.selectbox("Pitcher's Handedness", ["L", "R"])
    batter_vs_hand_avg = st.number_input("Batter AVG vs Handedness", format="%.4f")
    batter_vs_pitcher_avg = st.number_input("AVG vs Pitcher", format="%.4f")
    lineup_slot = st.number_input("Lineup Position (1-9)", min_value=1, max_value=9)

with col3:
    implied_probability = st.number_input("Implied Probability (%)", min_value=0.0, max_value=100.0)

# Calculate weighted average
weighted_avg = (
    0.4 * season_avg +
    0.25 * last7_avg +
    0.1 * vs_team_avg +
    0.15 * batter_vs_hand_avg +
    0.1 * batter_vs_pitcher_avg
)

# Binomial hit probability
ab = 4
hit_prob = 1 - (1 - weighted_avg) ** ab
ev = (hit_prob * 100) - implied_probability
true_pct = round(hit_prob * 100, 2)
implied_pct = implied_probability

# Determine Hit Zone
def hit_zone(prob):
    if prob >= 80:
        return "Elite"
    elif prob >= 70:
        return "Strong"
    elif prob >= 60:
        return "Moderate"
    else:
        return "Bad"

hit_zone_label = hit_zone(true_pct)

# Display results
st.subheader("📊 Player Hit Probability")
st.markdown(
    f"**Player:** {player_name}<br>"
    f"- **True Hit Probability:** {true_pct:.2f}%<br>"
    f"- **Implied Probability:** {implied_pct:.2f}%<br>"
    f"- **Expected Value (EV%):** {ev:.2f}%<br>"
    f"- **Hit Zone:** {hit_zone_label}",
    unsafe_allow_html=True
)

# Store hit board
if "hit_board" not in st.session_state:
    st.session_state.hit_board = []

if st.button("➕ Add to Hit Board"):
    st.session_state.hit_board.append({
        "Player": player_name,
        "True Probability (%)": true_pct,
        "Implied Probability (%)": implied_pct,
        "EV (%)": round(ev, 2),
        "Hit Zone": hit_zone_label
    })

# Display hit board
if st.session_state.hit_board:
    st.subheader("🏆 Top Hit Board")
    st.dataframe(pd.DataFrame(st.session_state.hit_board))

# Parlay builder
st.subheader("🎯 Parlay Builder (2-3 Legs)")
selected_players = st.multiselect("Select Players from Hit Board", [p["Player"] for p in st.session_state.hit_board])
if 2 <= len(selected_players) <= 3:
    product = 1
    for player in st.session_state.hit_board:
        if player["Player"] in selected_players:
            product *= player["True Probability (%)"] / 100
    parlay_prob = product
    parlay_ev = parlay_prob * 100 - sum([p["Implied Probability (%)"] for p in st.session_state.hit_board if p["Player"] in selected_players]) / len(selected_players)

    # Parlay Zone
    def parlay_zone(p):
        if p >= 65:
            return "Elite"
        elif p >= 55:
            return "Strong"
        elif p >= 45:
            return "Moderate"
        else:
            return "Bad"

    st.markdown(
        f"**Parlay True Probability:** {parlay_prob:.2%}  
"
        f"**Expected Value (EV%):** {parlay_ev:.2f}%  
"
        f"**Parlay Zone:** {parlay_zone(parlay_prob * 100)}"
    )
