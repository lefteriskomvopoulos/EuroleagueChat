# from euroleague_api.player_stats import PlayerStats
# from euroleague_api.team_stats import TeamStats
# from euroleague_api.boxscore_data import BoxScoreData
# from euroleague_api.standings import Standings

# class Neo4jConnection:

#     def __init__(self, uri, auth):

#         self.driver = GraphDatabase.driver(uri, auth = auth)

#     def close(self):
    
#         self.driver.close()

#     def add_player_to_team(self, player_name, team_name):

#         with self.driver.session() as session:
#             result = session.execute_write(
#                 self._create_and_link_player_team, player_name, team_name)
#             print(result)

#     @staticmethod
#     def _create_and_link_player_team(tx, player_name, team_name):
#         query = (
#             "MERGE (p:Player {player_name: $playerName}) "
#             "MERGE (t:Team {team_name: $teamName}) "
#             "MERGE (p)-[r:PLAYS_FOR]->(t) "
#             "RETURN p.name AS player, t.name AS team"
#         )
        
#         print(f"Executing query to link '{player_name}' to '{team_name}'...")
#         result = tx.run(query, playerName=player_name, teamName=team_name)
        
#         return result.single()

#     def add_stats_to_player(self, player_name, round, player_stats):

#         with self.driver.session() as session:
#             result = session.execute_write(
#                 self._create_and_link_player_stats, player_name, round, player_stats)
#             print(result)

#     @staticmethod
#     def _create_and_link_player_stats(tx, player_name, round, player_stats):
#         query = (
#             "MERGE (p:Player {player_name: $playerName}) "
#             "MERGE (s:Stats {game_round: $round, minutes_played: $minutes, performance: $pir}) "
#             "MERGE (p)-[r:PERFORMS]->(s) "
#             "RETURN p.name AS player, s.name AS stats"
#         )
        
#         print(f"Executing query to link '{player_name}' to '{player_stats}'...")
#         result = tx.run(query, playerName=player_name, round=round, minutes=player_stats['minutes'], pir=player_stats['valuation'])
        
#         return result.single()
    
#     def add_credits_to_player(self, player_name, credits):

#         with self.driver.session() as session:
#             result = session.execute_write(
#                 self._create_and_link_player_credits, player_name, credits)
#             print(result)

#     @staticmethod
#     def _create_and_link_player_credits(tx, player_name, credits):
#         query = (
#             "MERGE (p:Player {player_name: $playerName}) "
#             "MERGE (c:Credits {credits: $credits}) "
#             "MERGE (p)-[r:COSTS]->(c) "
#             "RETURN p.name AS player, c.name AS credits"
#         )
        
#         print(f"Executing query to link '{player_name}' to '{credits}'...")
#         result = tx.run(query, playerName=player_name, credits=credits)
        
#         return result.single()
    
# if LOAD_PLAYERS_TEAMS:
        
#     ### Fetch team statistics ###
#     teams = Standings()
#     teams_info = teams.get_standings(2025, 1)
#     teams_names = {}
#     for team_code, team_name in zip(teams_info['club.code'], teams_info['club.name']):
#         teams_names[team_code] = team_name

#     ### Fetch player statistics ###
#     games = BoxScoreData()
#     players_info = {}
#     players_stats = {}
#     for round in range(1, ROUND + 1):
#         print(f"Fetching stats for gamecode: {round}")
#         round_stats = games.get_player_boxscore_stats_round(2025, round)
#         for player_id, player_name, team, round, minutes, valuation in zip(round_stats['Player_ID'], round_stats['Player'], round_stats['Team'], round_stats['Round'], round_stats['Minutes'], round_stats['Valuation']):
#             if player_id not in players_stats:
#                 players_info[player_id] = {'name': player_name, 'team': teams_names[team]}
#                 players_stats[player_id] = {}
#             if pd.isna(minutes) or minutes == 'DNP':
#                 minutes = 0
#             else:
#                 minutes = int(minutes.split(':')[0]) + 1 
#             players_stats[player_id][round] = {'minutes': minutes, 'valuation': valuation}

#     ### JSON FORMATTING ###
#     # pretty_json_string = json.dumps(players_stats, indent=4)
#     # print(pretty_json_string)

#     ### UPLOAD TO NEO4J ###
#     for player in players_info:
#         conn.add_player_to_team(players_info[player]['name'], players_info[player]['team'])

#     for player in players_stats:
#         for round in players_stats[player]:
#             conn.add_stats_to_player(players_info[player]['name'], round, players_stats[player][round])

# if LOAD_CREDITS:

#     ### Load environment variables ###
#     dotenv.load_dotenv(override=True)
#     load_status = dotenv.load_dotenv("Neo4j-86d870c3-Created-2025-10-09.txt")
#     if load_status is False:
#         raise RuntimeError('Environment variables not loaded.')

#     URI = os.getenv("NEO4J_URI")
#     AUTH = (os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))

#     graph = Neo4jGraph()
#     graph.refresh_schema()

#     ### Fetch players from DB ###
#     query_for_players = """
#         MATCH (p:(Player))
#         RETURN DISTINCT p.player_name AS player_name
#     """
#     players = graph.query(query_for_players)
#     players = [player['player_name'] for player in players]

#     ### UPLOAD TO NEO4J ###
#     for player in players:
#         if player in fantasy_stats:
#             conn.add_credits_to_player(player, fantasy_stats[player])