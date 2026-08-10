import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Eredivisie 2026-2027 Analytics", layout="wide")

@st.cache_data(ttl=3600)
def load_data():
    players_df = pd.read_parquet("eredivisie_players_2026.parquet")
    news_df = pd.read_csv("transfers_news.csv")
    return players_df, news_df

try:
    players_df, news_df = load_data()
except Exception:
    st.warning("Data wordt momenteel geladen of gegenereerd... Vernieuw de pagina zo meteen.")
    st.stop()

st.title("⚽ Eredivisie 2026-2027 Analytics & Transfer Radar")
st.caption("Automatisch ververst na elke speelronde. Inclusief xG, xA en Expected Threat (xT).")

st.sidebar.header("🔍 Filters")
selected_team = st.sidebar.multiselect("Selecteer Team(s)", options=players_df["team"].unique(), default=players_df["team"].unique())
selected_pos = st.sidebar.multiselect("Selecteer Positie(s)", options=players_df["positie"].unique(), default=players_df["positie"].unique())
min_minutes = st.sidebar.slider("Minimaal Aantal Minuten", 0, 90, 0)

filtered_df = players_df[
    (players_df["team"].isin(selected_team)) & 
    (players_df["positie"].isin(selected_pos)) & 
    (players_df["minuten"] >= min_minutes)
]

tab1, tab2, tab3 = st.tabs(["📊 Spelers Analyse", "🛡️ Team Performance", "🔄 Transfers & Geruchten"])

with tab1:
    st.subheader("Onderliggende Spelersdata")
    metric_type = st.radio("Weergave:", ["Totaal", "Per 90 Minuten"], horizontal=True)
    
    if metric_type == "Per 90 Minuten":
        cols_to_show = ["speler", "team", "positie", "minuten", "xG_p90", "xA_p90", "xG+xA_p90", "xT_opbouw", "tackles_interceptions"]
        sort_col = "xG_p90"
    else:
        cols_to_show = ["speler", "team", "positie", "minuten", "goals", "assists", "xG", "xA", "xT_opbouw", "tackles_interceptions"]
        sort_col = "xG"
        
    st.dataframe(filtered_df[cols_to_show].sort_values(by=sort_col, ascending=False), use_container_width=True)
    
    fig = px.scatter(
        filtered_df, 
        x="xG_p90", 
        y="xA_p90", 
        text="speler", 
        color="positie", 
        size="minuten",
        title="Expected Goals (xG) vs Expected Assists (xA) Per 90"
    )
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Aanvallende vs Defensieve Dreiging per Team")
    team_summary = filtered_df.groupby("team")[["xG", "xA", "xT_opbouw", "tackles_interceptions"]].sum().reset_index()
    fig_team = px.bar(team_summary, x="team", y=["xG", "xA", "xT_opbouw"], title="Totale Team Opbouw & Dreiging", barmode="group")
    st.plotly_chart(fig_team, use_container_width=True)

with tab3:
    st.subheader("📰 Live Transfers & Nieuwsfeed")
    for _, row in news_df.iterrows():
        st.markdown(f"**[{row['titel']}]({row['link']})**")
        st.caption(f"Gepubliceerd: {row['gepubliceerd']}")
        st.divider()
