from nba_api.stats.static import players
from nba_api.stats.endpoints import playercareerstats
from nba_api.live.nba.endpoints import scoreboard
from nba_api.stats.endpoints import playergamelogs

def get_player_by_name(name):
    all_players = players.get_players()
    matched_players = [player for player in all_players if name.lower() in player['full_name'].lower()]
    return matched_players

def get_player_stats(player_id):
    career = playercareerstats.PlayerCareerStats(player_id=player_id)
    return career.get_data_frames()[0]

def get_player_last_10_stats(player_id):
    career = playergamelogs.PlayerGameLogs(
        player_id_nullable=player_id,
        season_nullable="2024-25",
        season_type_nullable="Regular Season",
        last_n_games_nullable=11
    )

    games = career.get_data_frames()[0]
    return games
def get_live_scoreboard(): 
    board = scoreboard.ScoreBoard()
    games = board.games.get_dict()
    return games
