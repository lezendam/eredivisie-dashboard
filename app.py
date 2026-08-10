import streamlit as st
import pandas as pd
import os
from fetch_data import fetch_eredivisie_data

st.set_page_config(page_title="Eredivisie Dashboard 2026/2027", layout="wide")

st.title("Dashboard (Seizoen 2026/2027)")
st.caption("Analyseer de prestatiestatistieken van alle 18 Eredivisie-teams en alle posities.")

@st.cache_data(ttl=3600)
def load_data():
    # 1. Probeer de nieuwste data op te halen via fetch_data
    try:
        df = fetch_eredivisie_data()
    except Exception as e:
        # Fallback naar opgeslagen bestand
        if os.path.exists("eredivisie_players_2026.parquet"):
            df = pd.read_parquet("eredivisie_players_2026.parquet")
        elif os.path.exists("eredivisie_players_2026.csv"):
            df = pd.read_csv("eredivisie_players_2026.csv")
        else:
            st.error("Geen data gevonden.")
            return pd.DataFrame()

    # 2. Corrigeer kolomnamen automatisch (hoofdletteronafhankelijk)
    renames = {
        "team": "Team",
        "speler": "Speler",
        "positie": "Positie",
        "goals": "Goals",
        "assists": "Assists",
        "minuten": "Minuten",
        "rugnummer": "Rugnummer"
    }
    df = df.rename(columns=renames)
    
    return df

df = load_data()

if not df.empty and "Team" in df.columns:
    # Filters in de sidebar
    st.sidebar.header("Filters")
    
    alle_teams = ["Alle teams"] + sorted(df["Team"].dropna().unique().tolist())
    gekozen_team = st.sidebar.selectbox("Selecteer Team", alle_teams)
    
    alle_posities = ["Alle posities"] + sorted(df["Positie"].dropna().unique().tolist()) if "Positie" in df.columns else ["Alle posities"]
    gekozen_positie = st.sidebar.selectbox("Selecteer Positie", alle_posities)
    
    # Filteren van de DataFrame
    filtered_df = df.copy()
    if gekozen_team != "Alle teams":
        filtered_df = filtered_df[filtered_df["Team"] == gekozen_team]
    if gekozen_positie != "Alle posities" and "Positie" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["Positie"] == gekozen_positie]
        
    # KPI metrics bovenaan
    col1, col2, col3 = st.columns(3)
    col1.metric("Totaal Spelers", len(filtered_df))
    if "Goals" in filtered_df.columns:
        col2.metric("Totaal Goals", int(filtered_df["Goals"].sum()))
    if "Assists" in filtered_df.columns:
        col3.metric("Totaal Assists", int(filtered_df["Assists"].sum()))

    st.markdown("---")
    
    # Tabelweergave
    st.subheader("Spelerstatistieken")
    st.dataframe(filtered_df, use_container_width=True)
else:
    st.warning("Er is op dit moment geen data beschikbaar om te tonen.")
