import os
from dotenv import load_dotenv
import dotenv
from openai import OpenAI
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.prompts import ChatPromptTemplate
from langchain.chains import RetrievalQA
from langchain.chains import GraphCypherQAChain
from langchain_community.graphs import Neo4jGraph
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_community.chains.graph_qa.prompts import CYPHER_GENERATION_PROMPT
import warnings

warnings.filterwarnings('ignore')

load_dotenv(override=True)
key = os.getenv("OPENAI_API_KEY")
org = os.getenv("OPENAI_ORG_ID")

client = OpenAI(
        api_key=key,
        organization=org
)

# load_status = dotenv.load_dotenv("Neo4j-86d870c3-Created-2025-10-09.txt")
# if load_status is False:
#     raise RuntimeError('Environment variables not loaded.')

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
llm = ChatOpenAI(model_name="gpt-5")

def create_web_rag_chain(url: str, model_name: str = None):
    print(f"Loading content ...")
    loader = WebBaseLoader(url)
    docs = loader.load()
    print("Content loaded successfully.")

    text_splitter = RecursiveCharacterTextSplitter()
    documents = text_splitter.split_documents(docs)

    embeddings = OpenAIEmbeddings()
    print("Creating vector store...")
    vector_store = FAISS.from_documents(documents, embeddings)
    print("Vector store created.")

    llm = ChatOpenAI(model_name=model_name)

    prompt = ChatPromptTemplate.from_template(
            """ This context includes stats about all the active players of Euroleague.
                Each column represents a different statistical category. For example, column 'PTS' comes for points, while FTM comes for Free Throws Made.
                Each column has an average (not a cumulative) value. 
                
                Answer the following question based only on the provided context:

                {context}

                Question: {question}
                
                Always justify your answer with the data included in the context. If you can't find the answer, say it clearly.
                Never make up an answer. If the question is not related to the context, politely respond that you are only able to answer questions that are related to the context."""
    )

    retriever = vector_store.as_retriever()
    
    qa = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={"prompt": prompt},
        input_key="question",
        output_key="answer",
    )

    print("RAG chain ready!")
    return qa

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
        model="gpt-5",
        messages=[{"role": "user", "content": formatted_prompt}],
        response_format={"type": "text"},
    )

    return response.choices[0].message.content

def questioning(question):

    QA_PROMPT_TEMPLATE = """
    You are a helpful AI assistant tasked with answering questions based on data from a graph database.

    Use the following context to answer the question at the end.
    If you don't know the answer, just say that you don't know. Do not try to make up an answer.
    If the context is empty, state that you could not find any results for the user's question.

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
    -   In case you are requested to choose/select/recommend a team of players provided some credits, based on a metric, then try to mazimize that metric by taking advantage as more credits as possible.
        For example, imagine you have 20 credits and you have to recommend a team of three players, maximizing the total performance. Then :
        Team1: [Player1: 6 credits and 15 performance, [Player2: 6 credits and 14 performance, [Player3: 7 credits and 13 performance] is better than :
        Team2: [Player1: 9 credits and 20 performance, [Player2: 10 credits and 21 performance]
        since total_performance(Team1) = 42 and total_performance(Team2) = 41, even if Team2 includes better players.
        In other words, the best team does not necessarily includes the best players, but actually maximizes the metric without exceeding the credits.
    """

    CYPHER_PROMPT = PromptTemplate(
        template=CYPHER_GENERATION_TEMPLATE,
        input_variables=["schema", "question"]
    )

    qa_chain = LLMChain(llm=llm, prompt=QA_PROMPT)
    cypher_generation_chain = LLMChain(llm=llm, prompt=CYPHER_PROMPT)
    schema = graph.schema

    cypher_chain = GraphCypherQAChain(
        graph=graph,
        graph_schema=schema,
        cypher_generation_chain=cypher_generation_chain,
        qa_chain=qa_chain,
        verbose=True,
        allow_dangerous_requests=True,
    )

    print(f"\nRunning Cypher QA chain with query: '{matching(graph, question, client)}'")
    result = cypher_chain.invoke({"query": matching(graph, question, client)})
    print(f"Cypher QA Chain Result: {result['result']}")

    return result['result']