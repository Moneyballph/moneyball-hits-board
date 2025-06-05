
import streamlit as st
import base64
import pandas as pd

# Set page config
st.set_page_config(page_title="Moneyball Phil: Daily Hit Probability Simulator", layout="wide")

# Load and display logo
st.image("moneyball_logo.png", width=200)

# Set background image using base64
def set_background(image_file):
    with open(image_file, "rb") as img:
        encoded = base64.b64encode(img.read()).decode()
    css = f'''
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{encoded}");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    </style>
    '''
    st.markdown(css, unsafe_allow_html=True)

set_background("baseball_diamond_bg.png")

st.title("Moneyball Phil: Daily Hit Probability Simulator")

# Player input
st.subheader("Enter Player Stats")
player_name = st.text_input("Player Name")
last7 = st.number_input("AVG Last 7 Days", min_value=0.0000, max_value=1.0000, format="%.4f")
home_away = st.number_input("AVG Home/Away", min_value=0.0000, max_value=1.0000, format="%.4f")
vs_league = st.number_input("AVG vs League (AL/NL)", min_value=0.0000, max_value=1.0000, format="%.4f")
vs_hand = st.number_input("AVG vs Pitcher Handedness", min_value=0.0000, max_value=1.0000, format="%.4f")
vs_pitcher = st.number_input("AVG vs Pitcher", min_value=0.0000, max_value=1.0000, format="%.4f")
pitcher_hand = st.selectbox("Pitcher's Throwing Hand", ["Right", "Left"])
batting_order = st.number_input("Expected Batting Spot (1–9)", min_value=1, max_value=9)

# Weighted average formula
weights = [0.3, 0.2, 0.2, 0.2, 0.1]
avgs = [last7, home_away, vs_league, vs_hand, vs_pitcher]
weighted_avg = sum([a * w for a, w in zip(avgs, weights)])

# Calculate hit probability
ab_estimate = 4  # base assumption
hit_prob = 1 - (1 - weighted_avg) ** ab_estimate

# Sportsbook odds input
st.subheader("Enter Sportsbook Odds")
odds = st.number_input("Sportsbook Odds (American)", value=-200)

# Calculate implied probability
if odds < 0:
    implied_pct = abs(odds) / (abs(odds) + 100)
else:
    implied_pct = 100 / (odds + 100)

ev = (hit_prob - implied_pct) * 100
hit_zone = "Elite" if hit_prob >= 0.80 else "Strong" if hit_prob >= 0.70 else "Moderate" if hit_prob >= 0.60 else "Bad"

# Hit board
st.subheader("Hit Probability Board")
st.markdown(f"- **Player:** {player_name}")
st.markdown(f"- **Weighted AVG:** {weighted_avg:.4f}")
st.markdown(f"- **True Hit Probability:** {hit_prob:.2%}")
st.markdown(f"- **Implied Probability:** {implied_pct:.2%}")
st.markdown(f"- **EV%:** {ev:+.2f}%")
st.markdown(f"- **Hit Zone:** {hit_zone}")

# Track players for parlay
if "parlay_players" not in st.session_state:
    st.session_state.parlay_players = []

if st.button("Add to Parlay"):
    st.session_state.parlay_players.append({
        "name": player_name,
        "true_prob": hit_prob,
        "implied_prob": implied_pct
    })

# Parlay builder
st.subheader("Parlay Builder")
selected_legs = st.multiselect("Select Players for Parlay", [p["name"] for p in st.session_state.parlay_players])

if selected_legs:
    selected_probs = [p["true_prob"] for p in st.session_state.parlay_players if p["name"] in selected_legs]
    parlay_prob = 1
    for prob in selected_probs:
        parlay_prob *= prob
    parlay_ev = parlay_prob - (1 / (1 + odds / 100)) if odds > 0 else parlay_prob - (abs(odds) / (abs(odds) + 100))
    zone = "Elite" if parlay_prob >= 0.65 else "Strong" if parlay_prob >= 0.55 else "Moderate" if parlay_prob >= 0.45 else "Bad"

    st.markdown(f"- **Parlay Legs:** {len(selected_probs)}")
    st.markdown(f"- **Parlay True Probability:** {parlay_prob:.2%}")
    st.markdown(f"- **EV vs Implied:** {parlay_ev:+.2f}")
    st.markdown(f"- **Parlay Zone:** {zone}")
