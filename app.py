import streamlit as st
import pandas as pd
import plotly.express as px
from fetch_data import fetch_eredivisie_data

# Pagina instellingen
st.set_page_config(
    page_title="Eredivisie Analytics 2026/2027",
    page_icon="⚽",
    layout="wide"
)

st.title("⚽ Eredivisie Player Analytics Dashboard (Seizoen 2026/2027)")
st.write("Analyseer de prestatiestatistieken van **alle 18 Eredivisie-teams** en **alle posities**.")

# Caching van data om laadsnelheid te optimaliseren
@st.cache_data(ttl=3600)
def load_data():
    return fetch_eredivisie_data()

df = load_data()

# --- SIDEBAR FILTERS ---
st.sidebar.header("🔍 Filters")

# Knop om alle filters direct te herstellen
if st.sidebar.button("🔄 Reset alle filters"):
    st.session_state.clear()
    st.rerun()

# 1. Team Filter
alle_teams = sorted(df["Team"].unique().tolist())
geselecteerde_teams = st.sidebar.multiselect(
    "Selecteer Team(s):",
    options=alle_teams,
    default=alle_teams,
    key="team_filter"
)

# 2. Positie Filter
alle_posities = sorted(df["Positie"].unique().tolist())
geselecteerde_posities = st.sidebar.multiselect(
    "Selecteer Positie(s):",
    options=alle_posities,
    default=alle_posities,
    key="positie_filter"
)

# 3. Zoekbalk op speler
zoek_speler = st.sidebar.text_input("Zoek op spelersnaam:", "", key="zoek_speler")

# 4. Filter op minimale speelminuten
min_minuten = int(df["Minuten"].min())
max_minuten = int(df["Minuten"].max())
gekozen_minuten = st.sidebar.slider(
    "Minimaal aantal speelminuten:",
    min_value=min_minuten,
    max_value=max_minuten,
    value=300,
    step=100,
    key="minuten_filter"
)

# --- FILTERING TOEPASSEN ---
df_filtered = df[
    (df["Team"].isin(geselecteerde_teams)) &
    (df["Positie"].isin(geselecteerde_posities)) &
    (df["Minuten"] >= gekozen_minuten)
]

if zoek_speler:
    df_filtered = df_filtered[df_filtered["Speler"].str.contains(zoek_speler, case=False, na=False)]

# Foutafhandeling wanneer geen spelers aan het filter voldoen
if df_filtered.empty:
    st.warning("⚠️ Geen spelers gevonden voor deze combinatie van filters. Verruim je filters in het menu links.")
else:
    # --- HIGHLIGHT CARDS (KPI'S) ---
    col1, col2, col3, col4 = st.columns(4)

    top_scorer = df_filtered.loc[df_filtered["Goals"].idxmax()]
    top_assist = df_filtered.loc[df_filtered["Assists"].idxmax()]
    top_xg = df_filtered.loc[df_filtered["xG"].idxmax()]
    top_tackles = df_filtered.loc[df_filtered["Tackles"].idxmax()]

    col1.metric("Topscorer", f"{top_scorer['Speler']} ({top_scorer['Team']})", f"{top_scorer['Goals']} Goals")
    col2.metric("Meeste Assists", f"{top_assist['Speler']} ({top_assist['Team']})", f"{top_assist['Assists']} Assists")
    col3.metric("Hoogste xG", f"{top_xg['Speler']} ({top_xg['Team']})", f"{top_xg['xG']} xG")
    col4.metric("Meeste Tackles", f"{top_tackles['Speler']} ({top_tackles['Team']})", f"{top_tackles['Tackles']} Tackles")

    st.markdown("---")

    # --- GRAFIEKEN TABBLADEN ---
    tab1, tab2, tab3 = st.tabs(["⚽ Aanval (xG vs Goals)", "🅰️ Creativiteit (xA vs Assists)", "🛡️ Verdediging (Tackles vs Interceptions)"])

    with tab1:
        st.subheader("Expected Goals (xG) vs Daadwerkelijke Goals")
        fig1 = px.scatter(
            df_filtered,
            x="xG",
            y="Goals",
            color="Team",
            hover_name="Speler",
            size="Minuten",
            text="Speler",
            title="Aanvallende efficiëntie (Grootte van bol = speelminuten)"
        )
        fig1.update_traces(textposition='top center')
        st.plotly_chart(fig1, use_container_width=True)

    with tab2:
        st.subheader("Expected Assists (xA) vs Daadwerkelijke Assists")
        fig2 = px.scatter(
            df_filtered,
            x="xA",
            y="Assists",
            color="Team",
            hover_name="Speler",
            size="Minuten",
            text="Speler",
            title="Creatieve impact (Grootte van bol = speelminuten)"
        )
        fig2.update_traces(textposition='top center')
        st.plotly_chart(fig2, use_container_width=True)

    with tab3:
        st.subheader("Verdedigende Acties (Tackles vs Onderscheppingen)")
        fig3 = px.scatter(
            df_filtered,
            x="Tackles",
            y="Interceptions",
            color="Team",
            hover_name="Speler",
            size="Minuten",
            text="Speler",
            title="Verdedigende intensiteit"
        )
        fig3.update_traces(textposition='top center')
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("---")

    # --- DATA TABEL ---
    st.subheader("📊 Volledige Spelersdatabank")
    st.dataframe(
        df_filtered.sort_values(by="Goals", ascending=False),
        use_container_width=True,
        column_config={
            "xG_per_90": st.column_config.NumberColumn("xG / 90 min", format="%.2f"),
            "xA_per_90": st.column_config.NumberColumn("xA / 90 min", format="%.2f"),
        }
    )

    # CSV Exporteren
    csv = df_filtered.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Gefilterde Data als CSV",
        data=csv,
        file_name="eredivisie_spelers_2026_2027.csv",
        mime="text/csv"
    )
