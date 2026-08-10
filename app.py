import streamlit as st
import pandas as pd
import os
from fetch_data import fetch_eredivisie_data

st.set_page_config(page_title="Eredivisie Dashboard 2026/2027", layout="wide")

st.title("Dashboard (Seizoen 2026/2027)")
st.caption("Analyseer de prestatiestatistieken van alle 18 Eredivisie-teams en alle posities.")

@st.cache_data(ttl=3600)
def load_data():
    try:
        df = fetch_eredivisie_data()
    except Exception:
        if os.path.exists("eredivisie_players_2026.parquet"):
            df = pd.read_parquet("eredivisie_players_2026.parquet")
        elif os.path.exists("eredivisie_players_2026.csv"):
            df = pd.read_csv("eredivisie_players_2026.csv")
        else:
            return pd.DataFrame()

    # Automatisch dubbele kolommen en hoofdletterverschillen herstellen
    df.columns = [str(col).capitalize() for col in df.columns]
    df = df.loc[:, ~df.columns.duplicated()]
    return df

df = load_data()

if not df.empty and "Team" in df.columns:
    st.sidebar.header("Filters")
    
    # Veilig de lijst met unieke teams ophalen
    team_series = df["Team"]
    if isinstance(team_series, pd.DataFrame):
        team_series = team_series.iloc[:, 0]
        
    alle_teams = ["Alle teams"] + sorted(team_series.dropna().astype(str).unique().tolist())
    gekozen_team = st.sidebar.selectbox("Selecteer Team", alle_teams)
    
    # Veilig de lijst met unieke posities ophalen
    if "Positie" in df.columns:
        pos_series = df["Positie"]
        if isinstance(pos_series, pd.DataFrame):
            pos_series = pos_series.iloc[:, 0]
        alle_posities = ["Alle posities"] + sorted(pos_series.dropna().astype(str).unique().tolist())
    else:
        alle_posities = ["Alle posities"]
        
    gekozen_positie = st.sidebar.selectbox("Selecteer Positie", alle_posities)
    
    # Filteren
    filtered_df = df.copy()
    if gekozen_team != "Alle teams":
        filtered_df = filtered_df[filtered_df["Team"] == gekozen_team]
    if gekozen_positie != "Alle posities" and "Positie" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["Positie"] == gekozen_positie]
        
    # KPI Statistieken
    col1, col2, col3 = st.columns(3)
    col1.metric("Totaal Spelers", len(filtered_df))
    if "Goals" in filtered_df.columns:
        col2.metric("Totaal Goals", int(pd.to_numeric(filtered_df["Goals"], errors='coerce').sum()))
    if "Assists" in filtered_df.columns:
        col3.metric("Totaal Assists", int(pd.to_numeric(filtered_df["Assists"], errors='coerce').sum()))

    st.markdown("---")
    
    st.subheader("Spelerstatistieken")
    st.dataframe(filtered_df, use_container_width=True)
else:
    st.warning("Er is op dit moment geen data beschikbaar om te tonen.")
