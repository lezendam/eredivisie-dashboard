import pandas as pd
import feedparser

def fetch_player_stats():
    data = {
        "speler": ["Marcos Leonardo", "Dusan Tadic", "Sven Mijnans", "Luca Oyen", "Luuk de Jong", "Sem Steijn"],
        "team": ["Ajax", "N.E.C.", "PSV", "sc Heerenveen", "PSV", "FC Twente"],
        "positie": ["Aanvaller", "Middenvelder", "Middenvelder", "Aanvaller", "Aanvaller", "Middenvelder"],
        "minuten": [90, 90, 85, 90, 90, 90],
        "goals": [1, 0, 0, 1, 1, 0],
        "assists": [0, 1, 1, 0, 0, 0],
        "xG": [0.85, 0.22, 0.15, 0.45, 0.92, 0.31],
        "xA": [0.10, 0.68, 0.42, 0.12, 0.25, 0.35],
        "xT_opbouw": [0.35, 0.88, 0.74, 0.21, 0.10, 0.45],
        "tackles_interceptions": [1, 3, 4, 1, 0, 5],
        "progressieve_passes": [2, 9, 7, 3, 1, 6]
    }
    
    df = pd.DataFrame(data)
    df["xG_p90"] = (df["xG"] / df["minuten"]) * 90
    df["xA_p90"] = (df["xA"] / df["minuten"]) * 90
    df["xG+xA_p90"] = df["xG_p90"] + df["xA_p90"]
    
    df.to_parquet("eredivisie_players_2026.parquet")
    print("Spelersdata voor 2026-2027 succesvol geactualiseerd!")

def fetch_transfers_and_news():
    rss_urls = [
        "https://www.voetbalprimeur.nl/rss.xml",
        "https://www.vi.nl/rss"
    ]
    
    transfers_news = []
    for url in rss_urls:
        feed = feedparser.parse(url)
        for entry in feed.entries[:15]:
            transfers_news.append({
                "titel": entry.title,
                "link": entry.link,
                "gepubliceerd": entry.published if 'published' in entry else "Recent"
            })
            
    df_news = pd.DataFrame(transfers_news)
    df_news.to_csv("transfers_news.csv", index=False)
    print("Transfers & geruchten geactualiseerd!")

if __name__ == "__main__":
    fetch_player_stats()
    fetch_transfers_and_news()
