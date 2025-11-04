import pandas as pd
import numpy as np
import requests

ROUND = 3

def weekly_stats(week):
    url = "https://www.dunkest.com/api/stats/table"

    params = {
        "season_id": 23,
        "mode": "dunkest",
        "stats_type": "avg",
        "weeks[]": week,
        "rounds[]": [1, 2, 3],
        "teams[]": [32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 56, 60, 75],
        "positions[]": [1, 2, 3],
        "player_search": "",
        "min_cr": 1,
        "max_cr": 30,
        "sort_by": "pdk",
        "sort_order": "desc",
        "iframe": "yes"
    }
    
    headers = {
        "accept": "application/json, text/javascript, */*; q=0.01",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "el-GR,el;q=0.9,en;q=0.8,es;q=0.7,de;q=0.6,it;q=0.5",
        "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Mobile Safari/537.36",
        "x-requested-with": "XMLHttpRequest"
    }
    
    response = requests.get(url, params=params, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
    else:
        print(f"Request failed with status code {response.status_code}")

    df=pd.DataFrame(data)

    return df

teams_ids = []
teams = []
players_ids = []
players = []
playersToTeams = []
stats = []
playersToStats = []
stat_id = 1
for round in range(1, 9):
    round_stats = weekly_stats(round)
    for index, row in round_stats.iterrows():
        if row['team_id'] not in teams_ids:
            teams_ids.append(row['team_id'])
            teams.append({'team_id': row['team_id'], 'team_name': row['team_name'], 'team_code': row['team_code']})
        playerToTeam = {'player_id': row['id'], 'team_id': row['team_id']}
        if row['id'] not in players_ids:
            players_ids.append(row['id'])
            players.append({'player_id': row['id'],
                            'player_name': row['first_name'] + " " + row['last_name'],
                            'position': row['position'],
                            'team_id': row['team_id']
            })
            playersToTeams.append(playerToTeam)  
        stats.append(   {'stat_id': stat_id,
                        'round': round,
                        'credits': float(row['cr']),
                        'fantasy_points': float(row['pdk']),
                        'plus/minus': float(row['plus_minus']),
                        'minutes': float(row['min']),
                        'starter': float(row['starter']),
                        'points' : float(row['pts']),
                        'assists': float(row['ast']),
                        'rebounds': float(row['reb']),
                        'offensive_rebounds': float(row['oreb']),
                        'defensive_rebounds': float(row['dreb']),
                        'steals': float(row['stl']),
                        'blocks': float(row['blk']),
                        'blocks_against': float(row['blka']),
                        'field_goals_made': float(row['fgm']),
                        'field_goals_attempted': float(row['fga']),
                        'three_points_made': float(row['tpm']),
                        'three_points_attempted': float(row['tpa']),
                        'free_throws_made': float(row['ftm']),
                        'free_throws_attempted': float(row['fta']),
                        'personal_fouls': float(row['pf']),
                        'fouls_received': float(row['fouls_received']),
                        'turnovers': float(row['tov'])
                        })
        playersToStats.append({'player_id': row['id'], 'stat_id': stat_id})
        stat_id += 1