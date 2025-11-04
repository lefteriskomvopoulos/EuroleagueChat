import os
from dotenv import load_dotenv
import dotenv
import pandas as pd
from openai import OpenAI
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import RetrievalQA
from langchain.chains import GraphCypherQAChain
from langchain_community.graphs import Neo4jGraph
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_community.chains.graph_qa.prompts import CYPHER_GENERATION_PROMPT
import warnings
from langchain.tools import tool
from langchain.agents import AgentExecutor, create_openai_tools_agent
from knapsack import knapSack, knapsack_multi_category

warnings.filterwarnings('ignore')

load_dotenv(override=True)
key = os.getenv("OPENAI_API_KEY")
org = os.getenv("OPENAI_ORG_ID")

client = OpenAI(
        api_key=key,
        organization=org
)

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
llm = ChatOpenAI(model_name="gpt-4o", temperature=0)

def matching(graph, question, client):
    query_for_teams = """
        MATCH (t:(Team))
        RETURN DISTINCT t.team_name AS team_name
    """
    teams = graph.query(query_for_teams)
    teams = [team['team_name'] for team in teams]

    query_for_players = """
        MATCH (p:(Player))
        RETURN DISTINCT p.player_name AS player_name
    """
    players = graph.query(query_for_players)
    players = [player['player_name'] for player in players]

    pre_prompt = PromptTemplate(
        input_variables=["question"],
        template="""
        Given a list of team_names :
        {teams}
        a list of player_names :
        {players}
        and a specific question:
        {question}
        proceed to these actions:
        1.  Identify if there is a name of team included in the question.
        2.  If there is no name, return the question unchanged.
        3.  If there is a name, then find its most relevant name from the list of team_names and then place it in the exact position of the old name in the question. Example : 'Which are the players of Olympiacos ?' => 'Which are the players of Olympiacos Piraeus ?'
        4.  Identify if there is a name of player included in the question.
        5.  If there is no name, return the question unchanged.
        6.  If there is a name, then find its most relevant name from the list of player_names and then place it in the exact position of the old name in the question. Example : 'How much points per game does Larkin have ?' => 'How much points per game does LARKIN, SHANE have ?'
        7.  In both cases, ALWAYS return ONLY the final question.
        8.  NEVER confuse players with teams. If you are not more than 70% sure, return the question unchanged.
        """
    )

    formatted_prompt = pre_prompt.format(teams=teams, players=players, question=question)
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": formatted_prompt}],
        response_format={"type": "text"},
    )

    return response.choices[0].message.content

print("Building GraphCypherQAChain...")
QA_PROMPT_TEMPLATE = """
You are a helpful AI assistant tasked with answering questions based on data from a graph database.

Use the following context to answer the question at the end.
If you don't know the answer, just say that you don't know. Do not try to make up an answer.
If the context is empty, state that you could not find any results for the user's question.

IMPORTANT NOTE:
- If you are asked to return the best set of players, given a limited amount of credits, then return this result:
(num_of_guards, num_of_forwards, num_of_centers, amount_of_credits), where
num_of_guards is the number of players that play as guards,
num_of_forwards is the number of players that play as forwards,
num_of_centers is the number of players that play as centers,
amount_of_credits is the number of credits the user said.
- DO NOT leave these four fields blank : num_of_guards = 4 (default), num_of_forwards = 4 (default), num_of_centers = 2 (default), num_of_credits = 100 (default).

Important about the answer format :
In case you are about to return a list (of players or teams etc) then use bullets.
Never include encouragement or proposal questions on how to continue.
Always return only the answer of the question.

Context:
{context}

Question: {question}
Helpful Answer:
"""
QA_PROMPT = PromptTemplate(
    template=QA_PROMPT_TEMPLATE,
    input_variables=["context", "question"]
)

CYPHER_GENERATION_TEMPLATE = CYPHER_GENERATION_PROMPT.template +"""
IMPORTANT:
-   You must generate only a single, valid Cypher query for the question. Do not generate multiple queries.
"""

CYPHER_PROMPT = PromptTemplate(
    template=CYPHER_GENERATION_TEMPLATE,
    input_variables=["schema", "question"]
)

qa_chain = LLMChain(llm=llm, prompt=QA_PROMPT)
cypher_generation_chain = LLMChain(llm=llm, prompt=CYPHER_PROMPT)
schema = graph.schema

graph_qa_chain = GraphCypherQAChain(
    graph=graph,
    graph_schema=schema,
    cypher_generation_chain=cypher_generation_chain,
    qa_chain=qa_chain,
    verbose=True,
    allow_dangerous_requests=True,
    top_k=50
)

print("GraphCypherQAChain ready.")

@tool
def dynamic_selection(query: str) -> str:
    """
    Use this tool to answer questions about selecting the best set of players
    based on a specific criterion and given a limited amount of credits.
    For example :
    'Which is the set of players with the total highest performance that I can buy with 50 credits'
    'Given 100 credits in total, tell me a team of 10 players in order to mazimize performance'
    'Recommend a team of 5 players with a budget of 100 credits.'
    """

    result = qa_chain.invoke({"question": query, "context": ""})
    guards = int(result['text'].split(", ")[0][1:])
    forwards = int(result['text'].split(", ")[1])
    centers = int(result['text'].split(", ")[2])
    position_limits = {'G': guards, 'F': forwards, 'C': centers}
    max_credits = int(result['text'].split(", ")[3][:-1])
    query_for_stats_and_credits = """
    MATCH (p:(Player))-[:Performs]->(s:(Stat))
    RETURN DISTINCT p.player_name AS player_name, s.fantasy_points AS player_performance, s.credits as player_credits, p.position as player_position
    """
    values = graph.query(query_for_stats_and_credits)
    df_values = pd.DataFrame(values)
    values = df_values.groupby('player_name').agg(value = ('player_performance', 'mean'), weight = ('player_credits', 'mean'), category = ('player_position', 'first')).reset_index().round(0).to_dict(orient='records')

    results = knapsack_multi_category(values, position_limits, max_credits)
    results = {result['player_name']: {'position': result['category'], 'credits': result['weight'], 'performance': result['value']} for result in results[1]}

    return results

@tool
def query_euroleague_graph_database(question: str) -> str:
    """
    Use this tool to answer questions about Euroleague players, teams, stats,
    and credits from the Neo4j graph database. For example:
    'Which players play for Olympiacos?'
    'How many points per game does LARKIN, SHANE have?'
    """
    matched_question = matching(graph, question, client)
    
    result = graph_qa_chain.invoke({"query": matched_question})
    
    return result['result']

tools = [
    dynamic_selection,
    query_euroleague_graph_database,
]

AGENT_SYSTEM_PROMPT = """
You are a helpful assistant. You have access to two specialized tools.
Based on the user's question, you must decide which tool is the most appropriate to use.
If the question is about Euroleague players, teams, or database stats, use 'query_euroleague_graph_database'.
If the question is about selecting the set of players with the higher performance, given a specific limit of credits, then use 'dynamic_selection'

Only use the output from the tool as your final answer. Do not add any extra text or pleasantries.

Your tools are:
- {tool_graph_qa}: {tool_graph_qa_desc}
- {tool_dynamic_sel}: {tool_dynamic_sel_desc}
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", AGENT_SYSTEM_PROMPT.format(
        tool_graph_qa=query_euroleague_graph_database.name,
        tool_graph_qa_desc=query_euroleague_graph_database.description,
        tool_dynamic_sel=dynamic_selection.name,
        tool_dynamic_sel_desc=dynamic_selection.description
    )),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

agent = create_openai_tools_agent(llm, tools, prompt)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True
)

if __name__ == "__main__":
    print("\n--- Agent is ready! Ask your questions. (Type 'exit' to quit) ---")
    
    chat_history = []
    
    while True:
        try:
            user_input = input("You: ")
            if user_input.lower() == 'exit':
                break
            
            response = agent_executor.invoke({
                "input": user_input,
                "chat_history": chat_history
            })
            
            output = response['output']
            print(f"Agent: {output}")
            
            chat_history.append(("human", user_input))
            chat_history.append(("ai", output))

        except Exception as e:
            print(f"An error occurred: {e}")
            print("Please try your question again.")