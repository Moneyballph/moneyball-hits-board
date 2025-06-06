
import streamlit as st
import base64
import pandas as pd

# Set up background
def set_background(img_file):
    with open(img_file, "rb") as f:
        img_bytes = f.read()
    encoded = base64.b64encode(img_bytes).decode()
    css = f'''
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{encoded}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    </style>
    '''
    st.markdown(css, unsafe_allow_html=True)

set_background("baseball_diamond_bg.png")

st.image("moneyball_logo.png", width=180)
st.title("💰 Moneyball Phil: Daily Hit Probability Simulator")

# Player Input
with st.form("player_form"):
    name = st.text_input("Player Name")
    season_avg = st.number_input("Season AVG", 0.0, 1.0, step=0.0001, format="%.4f")
    last7 = st.number_input("Last 7 Days AVG", 0.0, 1.0, step=0.0001, format="%.4f")
    split_avg = st.number_input("Split AVG (Home/Away or AL/NL)", 0.0, 1.0, step=0.0001, format="%.4f")
    hand_avg = st.number_input("AVG vs Pitcher Handedness", 0.0, 1.0, step=0.0001, format="%.4f")
    pitcher_avg = st.number_input("AVG vs Pitcher", 0.0, 1.0, step=0.0001, format="%.4f")
    odds = st.number_input("Sportsbook Odds (American)", step=1)
    submitted = st.form_submit_button("Calculate Player")

if "hit_board" not in st.session_state:
    st.session_state.hit_board = []

if submitted:
    weighted_avg = round(
        0.3 * last7 + 0.2 * split_avg + 0.2 * hand_avg + 0.1 * pitcher_avg + 0.2 * season_avg,
        4
    )
    true_prob = 1 - (1 - weighted_avg) ** 4
    if odds < 0:
        implied_prob = abs(odds) / (abs(odds) + 100)
    else:
        implied_prob = 100 / (odds + 100)
    ev = (true_prob - implied_prob) * 100
    zone = "Elite" if true_prob >= 0.80 else "Strong" if true_prob >= 0.70 else "Moderate" if true_prob >= 0.60 else "Bad"
    st.session_state.hit_board.append({
        "Player": name,
        "True Probability": round(true_prob * 100, 2),
        "Implied Probability": round(implied_prob * 100, 2),
        "EV%": round(ev, 2),
        "Zone": zone
    })

# Top Hit Board Display
if st.session_state.hit_board:
    st.subheader("🔥 Top Hit Board")
    df = pd.DataFrame(st.session_state.hit_board)
    st.dataframe(df, use_container_width=True)

# Parlay Builder
st.subheader("🎯 Parlay Builder (2-3 Legs)")
names = [player["Player"] for player in st.session_state.hit_board]
selected = st.multiselect("Select Players", names)

if 2 <= len(selected) <= 3:
    probs = [player["True Probability"] / 100 for player in st.session_state.hit_board if player["Player"] in selected]
    implieds = [player["Implied Probability"] / 100 for player in st.session_state.hit_board if player["Player"] in selected]
    joint_true = round((probs[0] * probs[1] * (probs[2] if len(probs) == 3 else 1)) * 100, 2)
    joint_implied = round((implieds[0] * implieds[1] * (implieds[2] if len(implieds) == 3 else 1)) * 100, 2)
    parlay_ev = round(joint_true - joint_implied, 2)
    parlay_zone = "Elite" if joint_true >= 80 else "Strong" if joint_true >= 70 else "Moderate" if joint_true >= 60 else "Bad"

    st.markdown(f"**True Parlay Probability:** {joint_true:.2f}%")
    st.markdown(f"**Implied Probability:** {joint_implied:.2f}%")
    st.markdown(f"**EV%:** {parlay_ev:+.2f}%")
    st.markdown(f"**Parlay Zone:** {parlay_zone}")
