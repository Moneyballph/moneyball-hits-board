
import streamlit as st
import math

st.set_page_config(layout="wide")

# Custom Background and Logo
page_bg_img = f'''
<style>
[data-testid="stAppViewContainer"] > .main {{
background-image: url("background.png");
background-size: cover;
background-position: center;
background-repeat: no-repeat;
background-attachment: fixed;
}}
</style>
'''
st.markdown(page_bg_img, unsafe_allow_html=True)
st.image("moneyball_logo.png", width=150)

st.title("Moneyball Phil: Daily Hit Probability Simulator")

# Parlay Builder Inputs
st.subheader("🔗 Parlay Builder")
leg1_prob = st.number_input("True Hit Probability for Leg 1 (%)", min_value=0.0, max_value=100.0, step=0.1) / 100
leg2_prob = st.number_input("True Hit Probability for Leg 2 (%)", min_value=0.0, max_value=100.0, step=0.1) / 100
leg3_prob = st.number_input("True Hit Probability for Leg 3 (%) [Optional]", min_value=0.0, max_value=100.0, step=0.1) / 100
parlay_odds = st.number_input("Sportsbook Parlay Odds (e.g. +150)", step=1)

if st.button("Calculate Parlay Value"):
    if leg3_prob > 0:
        true_parlay_prob = leg1_prob * leg2_prob * leg3_prob
    else:
        true_parlay_prob = leg1_prob * leg2_prob

    implied_prob = abs(parlay_odds) / (abs(parlay_odds) + 100) if parlay_odds > 0 else 100 / (100 + abs(parlay_odds))
    ev = (true_parlay_prob * (100 if parlay_odds < 0 else parlay_odds)) - (1 - true_parlay_prob) * 100

    # Determine Zone
    if true_parlay_prob > 0.8:
        parlay_zone = "Elite"
    elif true_parlay_prob > 0.7:
        parlay_zone = "Strong"
    elif true_parlay_prob > 0.6:
        parlay_zone = "Moderate"
    else:
        parlay_zone = "Bad"

    st.markdown(f"**True Parlay Probability:** `{true_parlay_prob * 100:.1f}%`")
    st.markdown(f"**Implied Probability:** `{implied_prob * 100:.1f}%`")
    st.markdown(f"**Expected Value (EV):** `{ev:.2f}%`")
    st.markdown("✅ This is a +EV Parlay!" if ev > 0 else "⚠️ Negative EV Bet")
    st.markdown(f"**Parlay Zone:** `{parlay_zone}`")
