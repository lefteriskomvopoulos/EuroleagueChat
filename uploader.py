from langchain_community.graphs import Neo4jGraph
from dotenv import load_dotenv
import os
import json
import pandas as pd
import retriever
import warnings

warnings.filterwarnings('ignore')
DELETING = 0
    
def upload_nodes(graph, data, node):
    query = f"""
        UNWIND $data AS node_props
        CREATE (n:{node})
        SET n = node_props
        RETURN count(n) AS nodes_created
    """

    return graph.query(query, {"data": data})

def upload_connections(graph, start_node_label, end_node_label, relationship_type, start_node_match_key, end_node_match_key, connections):
    query = f"""
    UNWIND $connections AS conn
    MATCH (start:{start_node_label} {{{start_node_match_key}: conn.{start_node_match_key}}})
    MATCH (end:{end_node_label} {{{end_node_match_key}: conn.{end_node_match_key}}})
    MERGE (start)-[r:{relationship_type}]->(end)
    RETURN count(r) AS relationships_created
    """

    return graph.query(query, {"connections": connections})

def deleteALL(graph):
    query = f"""
    MATCH (n) DETACH DELETE n;
    """

    return graph.query(query)

if __name__ == "__main__":

    load_dotenv(override=True)
    NEO4J_DATABASE = os.getenv("NEO4J_DATABASE")
    NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
    NEO4J_URI = os.getenv("NEO4J_URI")

    graph = Neo4jGraph(
        url=NEO4J_URI,
        username=NEO4J_USERNAME,
        password=NEO4J_PASSWORD,
        database=NEO4J_DATABASE
    )

    graph.refresh_schema()

    if DELETING:
        deleteALL(graph)
        print(f"Everything deleted")
        exit(0)

    teams = retriever.teams
    players = retriever.players
    playersToTeams = retriever.playersToTeams
    stats = retriever.stats
    playersToStats = retriever.playersToStats

    result = upload_nodes(graph, teams, "Team")
    print(f"Teams created: {result[0]['nodes_created']}")

    result = upload_nodes(graph, players, "Player")
    print(f"Players created: {result[0]['nodes_created']}")

    result = upload_connections(graph, "Player", "Team", "PlaysFor", "player_id", "team_id", playersToTeams)
    print(f"Connections created: {result[0]['relationships_created']}")

    result = 0
    for stat in stats:
        result += upload_nodes(graph, stat, "Stat")[0]['nodes_created']
    
    print(f"Stats created: {result}")

    result = upload_connections(graph, "Player", "Stat", "Performs", "player_id", "stat_id", playersToStats)
    print(f"Connections created: {result[0]['relationships_created']}")