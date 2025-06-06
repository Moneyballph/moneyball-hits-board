
import streamlit as st
from PIL import Image
import base64

# --- App Config ---
st.set_page_config(page_title="Moneyball Phil: Daily Hit Probability", layout="wide")

# --- Load Assets ---
logo = "moneyball_logo.png"
background = "background.png"

# --- Background Styling ---
def set_bg(image_file):
    with open(image_file, "rb") as img:
        data = base64.b64encode(img.read()).decode()
    bg_style = f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{data}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }}
        </style>
    """
    st.markdown(bg_style, unsafe_allow_html=True)

set_bg(background)
st.image(logo, width=250)

st.title("Moneyball Phil: Daily Hit Probability Dashboard")

# --- Player Input ---
st.header("🔍 Player Stat Entry")
player_name = st.text_input("Enter Player Name")
col1, col2, col3 = st.columns(3)
with col1:
    avg_last_7 = st.number_input("AVG Last 7 Days", min_value=0.0, max_value=1.0, step=0.001)
with col2:
    avg_split = st.number_input("Split AVG (home/away/etc)", min_value=0.0, max_value=1.0, step=0.001)
with col3:
    avg_vs_pitcher = st.number_input("AVG vs Pitcher", min_value=0.0, max_value=1.0, step=0.001)

# --- Weighted Average Calculation ---
weighted_avg = round((avg_last_7 * 0.4) + (avg_split * 0.3) + (avg_vs_pitcher * 0.3), 3)
st.markdown(f"### 🎯 Weighted AVG: `{weighted_avg}`")

# --- Hit Probability ---
true_prob = round(1 - (1 - weighted_avg) ** 4, 3)
implied_odds = st.number_input("Sportsbook Odds (American)", value=-185)
if implied_odds < 0:
    implied_pct = round(abs(implied_odds) / (abs(implied_odds) + 100), 3)
else:
    implied_pct = round(100 / (implied_odds + 100), 3)
ev = round((true_prob - implied_pct) * 100, 1)

# --- Hit Zone ---
if true_prob >= 0.80:
    zone = "🟩 Elite"
elif true_prob >= 0.70:
    zone = "🟨 Strong"
elif true_prob >= 0.60:
    zone = "🟧 Moderate"
else:
    zone = "🟥 Risky"

# --- Hit Board Display ---
st.header("📊 Top Hit Board")
st.markdown(f"""
| Rank | Player | True Hit % | Implied % | EV % | Hit Zone |
|------|--------|-------------|------------|--------|-----------|
| 1 | {player_name} | {true_prob:.2%} | {implied_pct:.2%} | {ev:+.1f}% | {zone} |
""")

# --- Parlay Builder ---
st.header("💥 Parlay Builder")
st.markdown("Enter hit probabilities for up to 3 players to build a custom parlay.")

p1 = st.number_input("Player 1 True Hit %", min_value=0.0, max_value=1.0, step=0.01)
p2 = st.number_input("Player 2 True Hit %", min_value=0.0, max_value=1.0, step=0.01)
p3 = st.number_input("Player 3 True Hit % (Optional)", min_value=0.0, max_value=1.0, step=0.01)

legs = [p for p in [p1, p2, p3] if p > 0]
if len(legs) >= 2:
    parlay_prob = 1
    for leg in legs:
        parlay_prob *= leg
    parlay_prob = round(parlay_prob, 4)

    if parlay_prob >= 0.75:
        pzone = "🟩 Elite Parlay"
    elif parlay_prob >= 0.60:
        pzone = "🟨 Strong Parlay"
    elif parlay_prob >= 0.45:
        pzone = "🟧 Moderate Parlay"
    else:
        pzone = "🟥 Risky Parlay"

    st.success(f"**Parlay True Probability:** {parlay_prob:.2%} — {pzone}")
