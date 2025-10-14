metrics = {'naive'      : 'average_performance',
           'classic'    : 'average_performance / credit',
           'weighted'   : 'last_performance * 0.5 / credit + average_performance * 0.5 / credit',
           'momentum'   : 'last_performance'}
cypher_query11 = "Which players play in Panathnaikos ?"
cypher_query1 = "In which team does Calinic play?"
cypher_query2 = "What is the average performance of Round 2 ?"
cypher_query3 = "What are the average playing minutes for those players who had more than 20 performance in round 1?"
cypher_query4 = "What is the average performance of players in Barcelona?"
cypher_query44 = "What is the average performance of Vezenkov?"
cypher_query5 = "How much credits does Walkup cost ?"
cypher_query55 = "How much credits do all the players of Olympiacos cost ?"
cypher_query6 = "Provide the best five players based on this metric : " + str(metrics['weighted'])
cypher_query7 = "Given you have 100 available credits to spend, choose the best set of 10 players based on this metric : " + str(metrics['classic'])
cypher_query77 = "Given you have 100 available credits to spend, choose the best set of 10 players based on this metric : " + str(metrics['naive'])