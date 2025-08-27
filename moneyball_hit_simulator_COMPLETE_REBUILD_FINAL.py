
# moneyball_phil_hit_simulator.py
# Moneyball Phil — Hit Probability Simulator
# Features:
# - Stable inputs (text_input for decimals)
# - Preview result -> Save to Board
# - Saved Player Board (delete / clear-all)
# - Parlay Builder (Saved Players only)
# - Client Share Mode: Read-only view + copy text + CSV download

import base64
import pandas as pd
import streamlit as st
from datetime import datetime

# --------------------------
# Page config + background
# --------------------------
st.set_page_config(page_title="Moneyball Phil Hit Simulator", layout="centered")

def set_background(image_file: str):
    try:
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
    except Exception:
        pass  # background optional

set_background("background.png")
try:
    st.image("moneyball_logo.png", width=180)
except Exception:
    pass

# --------------------------
# Session state
# --------------------------
if "saved_players" not in st.session_state:
    st.session_state.saved_players = []   # only players you choose to save
if "last_player_result" not in st.session_state:
    st.session_state.last_player_result = None
if "id_counter" not in st.session_state:
    st.session_state.id_counter = 1

def next_id():
    st.session_state.id_counter += 1
    return st.session_state.id_counter

# --------------------------
# Helpers
# --------------------------
def _to_float(txt: str, *, allow_empty=False, default=0.0):
    s = str(txt).strip()
    if allow_empty and s == "":
        return default
    return float(s)

def american_to_implied_from_text(txt: str) -> float:
    """
    Accept American odds like "-120" or "+110".
    Returns implied probability in [0,1].
    """
    s = str(txt).strip()
    if not s:
        raise ValueError("Odds are empty.")
    am = float(s.replace("+", ""))
    return abs(am) / (abs(am) + 100.0) if am < 0 else 100.0 / (am + 100.0)

def calculate_weighted_avg(season, last7, split_, hand, pitcher):
    return round(0.2 * season + 0.3 * last7 + 0.2 * split_ + 0.2 * hand + 0.1 * pitcher, 4)

def binomial_hit_probability(avg, ab=4):
    # P(at least one hit) with ab trials, success p=avg
    return round(1 - (1 - avg) ** ab, 4)

def classify_zone(prob):
    if prob >= 0.8:
        return "🟩 Elite"
    elif prob >= 0.7:
        return "🟨 Strong"
    elif prob >= 0.6:
        return "🟧 Moderate"
    else:
        return "🟥 Risky"

def saved_df():
    if not st.session_state.saved_players:
        return pd.DataFrame(columns=["id","name","true_prob","implied_prob","ev","zone","odds_txt"])
    return pd.DataFrame(st.session_state.saved_players)

def client_table(df: pd.DataFrame):
    out = df.copy()
    out = out[["name","true_prob","implied_prob","ev","zone","odds_txt"]].rename(columns={
        "name":"Player", "true_prob":"True %", "implied_prob":"Implied %", "ev":"EV %", "zone":"Zone", "odds_txt":"Odds"
    })
    out["True %"] = (out["True %"]*100).round(1)
    out["Implied %"] = (out["Implied %"]*100).round(1)
    out["EV %"] = out["EV %"].round(1)
    return out

def client_copy_text(df: pd.DataFrame):
    lines = []
    for _, r in df.iterrows():
        lines.append(f"{r['name']} — True {r['true_prob']*100:.1f}% | Imp {r['implied_prob']*100:.1f}% | EV {r['ev']:+.1f}% | {r['zone']} | {r['odds_txt']}")
    return "\n".join(lines)

# --------------------------
# Header + Client share mode toggle
# --------------------------
lcol, rcol = st.columns([1,1])
with lcol:
    st.title("💰 Moneyball Phil: Hit Probability Simulator")
with rcol:
    client_mode = st.toggle("Client Share Mode", value=False, help="Show read-only picks & parlay to share with clients")

# ==========================
# CLIENT MODE (read-only)
# ==========================
if client_mode:
    st.markdown("### 📌 Client Picks")
    df_saved = saved_df()
    if df_saved.empty:
        st.info("No saved players yet. Switch off Client Share Mode to add some.")
    else:
        # Client table
        display = client_table(df_saved)
        st.dataframe(display, use_container_width=True, hide_index=True)

        # Copy text + CSV download
        st.markdown("#### Share")
        txt = client_copy_text(df_saved)
        st.code(txt, language="text")
        csv_bytes = display.to_csv(index=False).encode()
        st.download_button("⬇️ Download CSV for Clients", data=csv_bytes, file_name="client_picks.csv", mime="text/csv")

        # Parlay Builder (Saved only)
        st.markdown("---")
        st.header("🧮 Parlay Builder (Saved Players)")
        names = [f"{p['id']} | {p['name']}" for p in st.session_state.saved_players]
        selected = st.multiselect("Select 2 or 3 Saved Players", names, key="parlay_select_client")

        if len(selected) in [2, 3]:
            ids_selected = [int(s.split("|",1)[0].strip()) for s in selected]
            subset = [p for p in st.session_state.saved_players if p["id"] in ids_selected]
            probs = [p["true_prob"] for p in subset]
            parlay_true = 1.0
            for p_true in probs:
                parlay_true *= p_true
            parlay_true = round(parlay_true, 4)

            st.markdown("### 📉 Sportsbook Parlay Odds (optional)")
            parlay_odds_txt = st.text_input(
                "Enter Combined Parlay Odds (American)",
                value="", key="parlay_odds_client", placeholder="+450 or -140"
            )
            try:
                implied_parlay_prob = american_to_implied_from_text(parlay_odds_txt) if parlay_odds_txt.strip() else None
            except ValueError as e:
                implied_parlay_prob = None
                st.warning(f"Could not parse parlay odds: {e}")

            if implied_parlay_prob is not None:
                parlay_ev = round((parlay_true - implied_parlay_prob) * 100.0, 1)
                st.markdown(f"**True Parlay Probability:** {parlay_true:.2%}")
                st.markdown(f"**Implied Parlay Probability:** {implied_parlay_prob:.2%}")
                st.markdown(f"**Parlay EV %:** {parlay_ev:+.1f}%")
            else:
                st.markdown(f"**True Parlay Probability:** {parlay_true:.2%}")
                st.caption("Enter American odds (e.g., +450 or -140) to see Implied % and EV.")
        elif len(selected) > 3:
            st.warning("Please select only 2 or 3 players.")
    st.stop()  # Hide editor parts in client mode

# ==========================
# EDITOR MODE (simulate + save)
# ==========================

# -------- Player input form --------
st.header("📥 Player Stat Entry")
with st.form("player_input"):
    name = st.text_input("Player Name", key="name")

    # Use text_input for decimals so typing/backspacing is never blocked
    season_avg_txt  = st.text_input("Season AVG", placeholder="0.285", key="season_avg")
    last7_avg_txt   = st.text_input("Last 7 Days AVG", placeholder="0.310", key="last7_avg")
    split_avg_txt   = st.text_input("Split AVG (Home/Away)", placeholder="0.295", key="split_avg")
    hand_avg_txt    = st.text_input("AVG vs Handedness", placeholder="0.305", key="hand_avg")
    pitcher_avg_txt = st.text_input("AVG vs Pitcher", placeholder="0.270", key="pitcher_avg")

    ab_vs_pitcher = st.number_input("At-Bats vs Pitcher", min_value=0, step=1, key="ab_vs_pitcher")

    pitcher_hand = st.selectbox("Pitcher Handedness", ["Right", "Left"], key="pitcher_hand")
    batting_order = st.selectbox("Batting Order Position", list(range(1, 10)), key="batting_order")

    odds_txt = st.text_input("Sportsbook Odds (American)", placeholder="-115", key="odds_txt")

    pitcher_era_txt  = st.text_input("Pitcher ERA", placeholder="3.75", key="pitcher_era")
    pitcher_whip_txt = st.text_input("Pitcher WHIP", placeholder="1.20", key="pitcher_whip")
    pitcher_k9_txt   = st.text_input("Pitcher K/9", placeholder="9.3", key="pitcher_k9")

    submit = st.form_submit_button("Simulate Player")

# -------- Compute on submit (preview until saved) --------
if submit:
    try:
        # Parse decimals
        season_avg  = _to_float(season_avg_txt)
        last7_avg   = _to_float(last7_avg_txt)
        split_avg   = _to_float(split_avg_txt)
        hand_avg    = _to_float(hand_avg_txt)
        pitcher_avg = _to_float(pitcher_avg_txt)

        odds_implied = american_to_implied_from_text(odds_txt)

        pitcher_era  = _to_float(pitcher_era_txt)
        pitcher_whip = _to_float(pitcher_whip_txt)
        pitcher_k9   = _to_float(pitcher_k9_txt)

        # Guards
        for label, val in [
            ("Season AVG", season_avg), ("Last 7 AVG", last7_avg), ("Split AVG", split_avg),
            ("AVG vs Hand", hand_avg), ("AVG vs Pitcher", pitcher_avg),
            ("Pitcher ERA", pitcher_era), ("Pitcher WHIP", pitcher_whip), ("Pitcher K/9", pitcher_k9),
        ]:
            if val < 0:
                raise ValueError(f"{label} cannot be negative.")
    except ValueError as e:
        st.error(f"Input error: {e}")
        st.session_state.last_player_result = None
    else:
        weighted_avg = calculate_weighted_avg(season_avg, last7_avg, split_avg, hand_avg, pitcher_avg)

        # Pitcher difficulty adjustment
        if pitcher_whip >= 1.40 or pitcher_era >= 5.00:
            adjustment = 0.020
            tier_pitcher = "🟢 Easy Pitcher"
        elif pitcher_whip < 1.10 or pitcher_era < 3.50:
            adjustment = -0.020
            tier_pitcher = "🔴 Tough Pitcher"
        else:
            adjustment = 0.000
            tier_pitcher = "🟨 Average Pitcher"

        adj_weighted_avg = round(max(0.0, min(1.0, weighted_avg + adjustment)), 4)

        # Estimated AB by batting order
        ab_lookup = {1: 4.6, 2: 4.5, 3: 4.4, 4: 4.3, 5: 4.2, 6: 4.0, 7: 3.8, 8: 3.6, 9: 3.4}
        est_ab = ab_lookup.get(batting_order, 4.0)
        true_prob = binomial_hit_probability(adj_weighted_avg, ab=round(est_ab))

        implied_prob = round(odds_implied, 4)
        ev = round((true_prob - implied_prob) * 100.0, 1)
        zone = classify_zone(true_prob)

        st.session_state.last_player_result = {
            "id": next_id(),
            "name": name or "Player",
            "pitcher_hand": pitcher_hand,
            "batting_order": batting_order,
            "weighted_avg": weighted_avg,
            "adj_avg": adj_weighted_avg,
            "est_ab": est_ab,
            "true_prob": true_prob,
            "implied_prob": implied_prob,
            "ev": ev,
            "zone": zone,
            "odds_txt": odds_txt.strip(),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

# -------- Preview + Save --------
if st.session_state.last_player_result:
    r = st.session_state.last_player_result
    st.markdown("---")
    st.subheader("🧪 Latest Simulation (Preview)")

    c1, c2, c3 = st.columns(3)
    c1.metric("Adjusted AVG", f"{r['adj_avg']:.3f}")
    c2.metric("Est. AB", f"{r['est_ab']:.1f}")
    c3.metric("Pitcher Tier", "Easy" if r["adj_avg"] > r["weighted_avg"] else ("Tough" if r["adj_avg"] < r["weighted_avg"] else "Average"))

    st.write(f"**Player:** {r['name']}  |  **Pitcher Hand:** {r['pitcher_hand']}  |  **Batting Order:** {r['batting_order']}")
    st.write(f"**Weighted AVG (pre-adj):** `{r['weighted_avg']}`  →  **Adjusted:** `{r['adj_avg']}`")
    st.write(f"**True Hit %:** {r['true_prob']*100:.1f}%  |  **Implied %:** {r['implied_prob']*100:.1f}%  |  **EV %:** {r['ev']:+.1f}%  |  **Odds:** {r['odds_txt']}")
    st.write(f"**Zone:** {r['zone']}")

    sc1, sc2, _ = st.columns([1,1,5])
    if sc1.button("💾 Save to Board", key=f"save_current_{r['id']}"):
        sig = (r["name"], r["odds_txt"], f"{r['true_prob']:.4f}")
        if not any((sp.get("sig") == sig) for sp in st.session_state.saved_players):
            row = r.copy()
            row["sig"] = sig
            st.session_state.saved_players.append(row)
            st.success(f"Saved {r['name']} to board.")
        else:
            st.info("That player/result is already on your board.")
    if sc2.button("Clear Preview", key="clear_preview"):
        st.session_state.last_player_result = None

# -------- Saved Player Board (editable) --------
st.markdown("---")
st.header("📌 Saved Player Board")

top_cols = st.columns([1, 1, 6])
if top_cols[0].button("🧹 Clear All Saved", key="clear_all_saved"):
    st.session_state.saved_players = []
    st.success("Cleared all saved players.")
if top_cols[1].button("⤴️ Copy CSV Preview", key="copy_csv_preview"):
    if st.session_state.saved_players:
        df_export = saved_df()
        st.code(df_export[["name","true_prob","implied_prob","ev","zone","odds_txt"]].to_csv(index=False), language="text")
    else:
        st.info("No saved players to export.")

if not st.session_state.saved_players:
    st.info("No saved players yet. Run a simulation and click **Save to Board**.")
else:
    header = st.columns([0.6, 2.2, 1, 1, 1, 1.2, 0.9, 1.2])
    header[0].write("**ID**")
    header[1].write("**Player**")
    header[2].write("**True %**")
    header[3].write("**Implied %**")
    header[4].write("**EV %**")
    header[5].write("**Zone**")
    header[6].write("**Odds**")
    header[7].write("**Delete**")

    for row in list(st.session_state.saved_players):
        cols = st.columns([0.6, 2.2, 1, 1, 1, 1.2, 0.9, 1.2])
        cols[0].write(str(row["id"]))
        cols[1].write(row["name"])
        cols[2].write(f"{row['true_prob']*100:.1f}%")
        cols[3].write(f"{row['implied_prob']*100:.1f}%")
        cols[4].write(f"{row['ev']:+.1f}%")
        cols[5].write(row["zone"])
        cols[6].write(row["odds_txt"])
        if cols[7].button("🗑️", key=f"del_saved_{row['id']}"):
            st.session_state.saved_players = [p for p in st.session_state.saved_players if p["id"] != row["id"]]
            st.success(f"Removed {row['name']} from board.")
            st.experimental_rerun()

# -------- Parlay Builder (Saved only) --------
st.markdown("---")
st.header("🧮 Parlay Builder (Saved Players Only)")

if len(st.session_state.saved_players) < 2:
    st.info("Save at least two players to build a parlay.")
else:
    names = [f"{p['id']} | {p['name']}" for p in st.session_state.saved_players]
    selected = st.multiselect("Select 2 or 3 Saved Players", names, key="parlay_select_saved")

    if len(selected) in [2, 3]:
        ids_selected = [int(s.split("|",1)[0].strip()) for s in selected]
        subset = [p for p in st.session_state.saved_players if p["id"] in ids_selected]
        probs = [p["true_prob"] for p in subset]

        parlay_true = 1.0
        for p_true in probs:
            parlay_true *= p_true
        parlay_true = round(parlay_true, 4)

        st.markdown("### 📉 Sportsbook Parlay Odds (optional)")
        parlay_odds_txt = st.text_input(
            "Enter Combined Parlay Odds (American)",
            value="", key="parlay_odds_saved_txt",
            placeholder="+450 or -140"
        )

        try:
            implied_parlay_prob = american_to_implied_from_text(parlay_odds_txt) if parlay_odds_txt.strip() else None
        except ValueError as e:
            implied_parlay_prob = None
            st.warning(f"Could not parse parlay odds: {e}")

        if implied_parlay_prob is not None:
            parlay_ev = round((parlay_true - implied_parlay_prob) * 100.0, 1)
            st.markdown(f"**True Parlay Probability:** {parlay_true:.2%}")
            st.markdown(f"**Implied Parlay Probability:** {implied_parlay_prob:.2%}")
            st.markdown(f"**Parlay EV %:** {parlay_ev:+.1f}%")
        else:
            st.markdown(f"**True Parlay Probability:** {parlay_true:.2%}")
            st.caption("Enter American odds (e.g., +450 or -140) to see Implied % and EV.")
    elif len(selected) > 3:
        st.warning("Please select only 2 or 3 players.")

