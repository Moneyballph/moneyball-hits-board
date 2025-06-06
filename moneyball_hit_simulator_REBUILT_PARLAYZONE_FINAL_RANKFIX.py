
# placeholder header...

st.header("🔥 Top Hit Board")
if st.session_state.players:
    df = pd.DataFrame(st.session_state.players)
    df = df.sort_values("true_prob", ascending=False).reset_index(drop=True)
    df.insert(0, "Rank", df.index + 1)
    df["True Prob %"] = (df["true_prob"] * 100).round(1)
    df["Implied %"] = (df["implied_prob"] * 100).round(1)
    df["EV %"] = df["ev"]
    st.dataframe(df[["Rank", "name", "True Prob %", "Implied %", "EV %", "zone"]], use_container_width=True)
else:
    st.info("No players yet.")
