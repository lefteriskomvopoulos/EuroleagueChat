import pandas as pd
import numpy as np
import requests

ROUND = 3

def weekly_stats(week):
    url = "https://www.dunkest.com/api/stats/table"

    # Define the query parameters as a dictionary
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
    
    # Define the headers for the request
    headers = {
        "accept": "application/json, text/javascript, */*; q=0.01",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "el-GR,el;q=0.9,en;q=0.8,es;q=0.7,de;q=0.6,it;q=0.5",
        "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Mobile Safari/537.36",
        "x-requested-with": "XMLHttpRequest"
    }
    
    # Make the GET request
    response = requests.get(url, params=params, headers=headers)
    
    # Check the response status
    if response.status_code == 200:
        # print("Request was successful!")
        data = response.json()  # Parse the JSON response
        # print(data)  # Print or handle the data as needed
    else:
        print(f"Request failed with status code {response.status_code}")

    df=pd.DataFrame(data)

    return df

weekly_df = pd.DataFrame()
for round in range(1, ROUND + 1):
    tmp = weekly_stats(round)
    tmp['week'] = round
    weekly_df = pd.concat([weekly_df,tmp])

weekly_df['pdk'] = weekly_df['pdk'].astype(float)
weekly_df['cr'] = weekly_df['cr'].astype(float)
weekly_df.sort_values(['id', 'week'], inplace = True)

fantasy_stats = {}
for player_first_name, player_last_name, team, cr, week in zip(weekly_df['first_name'], weekly_df['last_name'], weekly_df['team_name'], weekly_df['cr'], weekly_df['week']):
    fantasy_stats[str(player_last_name).upper() + ", " + str(player_first_name).upper()] = cr

