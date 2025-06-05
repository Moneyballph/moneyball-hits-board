
import streamlit as st
import pandas as pd
import base64

# --- Set up background and logo ---
def add_bg_and_logo():
    with open("baseball_diamond_bg.png", "rb") as bg_file:
        bg_bytes = bg_file.read()
        bg_base64 = base64.b64encode(bg_bytes).decode()
    page_bg_img = f'''
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{bg_base64}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    </style>
    '''
    st.markdown(page_bg_img, unsafe_allow_html=True)
    st.image("moneyball_logo.png", width=160)

add_bg_and_logo()

# --- App Title ---
st.title("💰 Moneyball Phil: Daily Hit Probability Simulator")

# --- Player Stat Inputs ---
st.header("Enter Player Stats")
col1, col2 = st.columns(2)
with col1:
    player_name = st.text_input("Player Name")
    avg_last7 = st.number_input("AVG - Last 7 Days", step=0.0001, format="%.4f")
    avg_vs_hand = st.number_input("AVG vs Handedness", step=0.0001, format="%.4f")
    avg_venue = st.number_input("AVG in Venue (Home/Away)", step=0.0001, format="%.4f")
with col2:
    pitcher_hand = st.selectbox("Pitcher's Handedness", ["Left", "Right"])
    batter_spot = st.slider("Batting Order Spot", 1, 9, 1)
    pitcher_avg = st.number_input("Batter AVG vs Pitcher", step=0.0001, format="%.4f")

# --- Weighting Formula ---
if st.button("Calculate Weighted AVG"):
    avg = (avg_last7 * 0.30 + avg_vs_hand * 0.30 + avg_venue * 0.20 + pitcher_avg * 0.20)
    st.success(f"Weighted Batting AVG: {avg:.4f}")

    # --- Binomial Model (4 ABs) ---
    prob_hit = 1 - (1 - avg) ** 4
    st.markdown(f"**True Hit Probability (4 ABs): `{prob_hit:.2%}`**")

    # --- Odds Input + EV + Implied % ---
    odds_input = st.text_input("Sportsbook Odds (e.g., -185 or +120)")
    if odds_input:
        try:
            odds = int(odds_input)
            implied = (abs(odds) / (abs(odds) + 100)) if odds < 0 else (100 / (odds + 100))
            implied_pct = implied
            ev = (prob_hit - implied_pct) / implied_pct * 100
            hit_zone = "Elite" if prob_hit > 0.80 else "Strong" if prob_hit > 0.70 else "Moderate" if prob_hit > 0.60 else "Bad"
            st.markdown(
                f"- **Implied Probability:** {implied_pct:.2%}  
"
                f"- **Expected Value (EV%):** `{ev:.1f}%`  
"
                f"- **Hit Zone:** `{hit_zone}`"
            )
        except:
            st.warning("Invalid odds input")

# --- Parlay Builder ---
st.header("Parlay Builder (2–3 Legs)")
legs = st.slider("Number of Legs", 2, 3, 2)
parlay_probs = []
parlay_names = []
for i in range(1, legs + 1):
    with st.expander(f"Parlay Leg {i}"):
        name = st.text_input(f"Player {i} Name", key=f"name_{i}")
        true_prob = st.number_input(f"True Probability (0.00 - 1.00)", min_value=0.0, max_value=1.0, step=0.0001, key=f"tp_{i}")
        implied_odds = st.text_input(f"Sportsbook Odds", key=f"odds_{i}")
        if implied_odds:
            try:
                odds = int(implied_odds)
                implied = (abs(odds) / (abs(odds) + 100)) if odds < 0 else (100 / (odds + 100))
                ev = (true_prob - implied) / implied * 100
                parlay_probs.append(true_prob)
                parlay_names.append((name, true_prob, implied, ev))
            except:
                st.warning("Invalid odds format")

if st.button("Simulate Parlay"):
    if len(parlay_probs) == legs:
        from functools import reduce
        from operator import mul
        joint_true = reduce(mul, parlay_probs)
        joint_implied = reduce(mul, [p[2] for p in parlay_names])
        parlay_ev = (joint_true - joint_implied) / joint_implied * 100
        zone = "Elite" if joint_true > 0.80 else "Strong" if joint_true > 0.70 else "Moderate" if joint_true > 0.60 else "Bad"
        st.subheader("Parlay Simulation Result")
        st.write(f"✅ True Probability: `{joint_true:.2%}`")
        st.write(f"📉 Implied Probability: `{joint_implied:.2%}`")
        st.write(f"📈 Expected Value (EV%): `{parlay_ev:.1f}%`")
        st.write(f"🏆 Parlay Strength Zone: `{zone}`")
    else:
        st.warning("Please complete all legs with valid entries.")
