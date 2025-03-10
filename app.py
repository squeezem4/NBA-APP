from flask import Flask, render_template, request, redirect, url_for
import nba_stats
import pandas as pd
from nba_api.stats.endpoints import Scoreboard
from datetime import datetime, timezone
from dateutil import parser
import plotly.express as px

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    players = None
    search_term = None
    if request.method == "POST":
        search_term = request.form.get("player_name")
        if search_term:
            players = nba_stats.get_player_by_name(search_term)
    # Get live games from your nba_stats module
    games = nba_stats.get_live_scoreboard()
    games_list = []
    for game in games:
        # Convert the game time to local time zone
        gameTimeLTZ = parser.parse(game["gameTimeUTC"]).replace(tzinfo=timezone.utc).astimezone(tz=None)
        games_list.append({
            "awayTeam": game['awayTeam']['teamName'],
            "homeTeam": game['homeTeam']['teamName'],
            "time": gameTimeLTZ.strftime('%I:%M %p')
        })
    return render_template("index.html", players=players, search_term=search_term, games=games_list)
def player_averages(player_id):
    stats = nba_stats.get_player_stats(player_id)
    stats = stats[stats["SEASON_ID"] == "2024-25"]
    points = stats['PTS']
    rebounds = stats['REB']
    assists = stats['AST']
    games = stats['GP']
    avgPoints = float(points / games)
    avgRebounds = float(rebounds / games)
    avgAssists = float(assists / games)
    return avgPoints, avgRebounds, avgAssists
    
@app.route("/player/<player_id>")
def player_stats(player_id):
    player = nba_stats.playercareerstats.PlayerCareerStats(player_id=player_id)
    stats = nba_stats.get_player_stats(player_id)
    last10Games = nba_stats.get_player_last_10_stats(player_id)
    last10Games["GAME_DATE"] = pd.to_datetime(last10Games["GAME_DATE"]).dt.strftime("%m/%d")
    last10Games.reset_index(drop=True, inplace=True)
    stats.reset_index(drop=True, inplace=True)
    last10Games.insert(0, "Games", range(1, len(last10Games) + 1))
    stats.insert(0, "Season #", range(1, len(stats) + 1))
    # If stats is a DataFrame, convert it to HTML
    stats.drop(columns=['PLAYER_ID','TEAM_ID', 'LEAGUE_ID'], inplace=True, errors='ignore')
    table = stats.to_html(classes="table table-striped" , index=False) if hasattr(stats, "to_html") else stats
    #last_10_table = last10Games.to_html(classes="table table-striped", index=False) if hasattr(last10Games, "to_html") else last10Games
    avgPoints, avgRebounds, avgAssists = player_averages(player_id)

    matchups = last10Games.apply(lambda row: f"{row['MATCHUP']}", axis=1).tolist()
    dates = last10Games.apply(lambda row: f"{row['GAME_DATE']}", axis=1).tolist()
    for i in range(len(matchups)):
        if '@' in matchups[i]:
            matchups[i] = matchups[i][-5:]
        else:
            matchups[i] = matchups[i][-7:]

    pointsFig = px.bar(last10Games, x="Games", y="PTS", title="Points in last 10 Games", text_auto='.2s', barmode="group")
    pointsFig.update_layout(
        xaxis=dict(
            tickmode='array',
            tickvals=list(range(1, len(last10Games)+1)),
            ticktext=[f"{matchups[i]}<br>{dates[i]}" for i in range(len(matchups))],
            tickangle = 0
        )
    )
    pointsGraphJSON = pointsFig.to_html(full_html=False)
    
    reboundsFig = px.bar(last10Games, x="Games", y="REB", title="Rebounds in last 10 Games", text_auto='.2s', barmode="group")
    reboundsFig.update_layout(
        xaxis=dict(
            tickmode='array',
            tickvals=list(range(1, len(last10Games)+1)),
            ticktext=[f"{matchups[i]}<br>{dates[i]}" for i in range(len(matchups))],
            tickangle = 0
        )
    )
    reboundsGraphJSON = reboundsFig.to_html(full_html=False)

    assistsFig = px.bar(last10Games, x="Games", y="AST", title="Assists in last 10 Games", text_auto='.2s', barmode="group")
    assistsFig.update_layout(
        xaxis=dict(
            tickmode='array',
            tickvals=list(range(1, len(last10Games)+1)),
            ticktext=[f"{matchups[i]}<br>{dates[i]}" for i in range(len(matchups))],
            tickangle = 0
        )
    )
    assistsGraphJSON = assistsFig.to_html(full_html=False)

    shootPercentFig = px.bar(last10Games, x="Games", y="FG_PCT", title="Shooting Percentage in last 10 Games", text_auto='.3s', barmode="group")
    shootPercentFig.update_layout(
        xaxis=dict(
            tickmode='array',
            tickvals=list(range(1, len(last10Games)+1)),
            ticktext=[f"{matchups[i]}<br>{dates[i]}" for i in range(len(matchups))],
            tickangle = 0
        )
    )
    shootPercentGraphJSON = shootPercentFig.to_html(full_html=False)
    return render_template("player_stats.html", 
                           player=player,
                           table=table,
                           pointsGraphJSON=pointsGraphJSON,
                           reboundsGraphJSON=reboundsGraphJSON,
                           assistsGraphJSON=assistsGraphJSON,
                           shootPercentGraphJSON=shootPercentGraphJSON,
                           avgPoints=avgPoints,
                           avgRebounds=avgRebounds,
                           avgAssists=avgAssists)
#last_10_table=last_10_table,

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

