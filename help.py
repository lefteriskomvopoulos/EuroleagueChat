    ################################
    ### Simple OpenAI Example ###
    ################################

    # client = OpenAI(
    #     api_key=key,
    #     organization=org
    # )
    # response = client.chat.completions.create(
    #     model="gpt-5-nano",
    #     messages=[{"role": "user", "content": "Hello! What is the weather like today?"}],
    #     response_format={"type": "text"},
    #     verbosity="medium",
    #     reasoning_effort="medium",
    #     store=False,
    # )
    # print(response)

    ######################################
    ### Langchain Example with Webpage ###
    ######################################
    
    # # webpage_url = "https://www.euroleaguebasketball.net/euroleague/stats/players/?size=1000&viewType=traditional&statisticMode=perGame&seasonCode=E2025&seasonMode=Single&sortDirection=descending"
    # webpage_url = "https://euroleaguefantasy.euroleaguebasketball.net/10/stats"
    # rag_chain = create_web_rag_chain(webpage_url, model_name="gpt-3.5-turbo-0125")

    # question = "How much points per game does Calinic have? Also how much PIR does he average?"
    # # question = "What are the stats of Spanoulis ?"

    # print(f"\nAsking question: {question}")

    # try:
    #     result = rag_chain.invoke({"question": question})
    # except Exception as e:
    #     raise RuntimeError(f"Chain invocation failed: {e}")

    # if isinstance(result, dict):
    #     answer = next(
    #         (result[k] for k in ("output_text", "answer", "result", "output", "text") if k in result),
    #         next(iter(result.values()), ""),
    #     )
    # else:
    #     answer = result

    # print("\n--- Answer ---")
    # print(answer)

    ######################################
    #####  RAG Example with Webpage  #####
    ######################################
    # def create_web_rag_chain(url: str, model_name: str = None):
    #     print(f"Loading content ...")
    #     loader = WebBaseLoader(url)
    #     docs = loader.load()
    #     print("Content loaded successfully.")

    #     text_splitter = RecursiveCharacterTextSplitter()
    #     documents = text_splitter.split_documents(docs)

    #     embeddings = OpenAIEmbeddings()
    #     print("Creating vector store...")
    #     vector_store = FAISS.from_documents(documents, embeddings)
    #     print("Vector store created.")

    #     llm = ChatOpenAI(model_name=model_name, temperature=1)

    #     prompt = ChatPromptTemplate.from_template(
    #             """ This context includes stats about all the active players of Euroleague.
    #                 Each column represents a different statistical category. For example, column 'PTS' comes for points, while FTM comes for Free Throws Made.
    #                 Each column has an average (not a cumulative) value. 
                    
    #                 Answer the following question based only on the provided context:

    #                 {context}

    #                 Question: {question}
                    
    #                 Always justify your answer with the data included in the context. If you can't find the answer, say it clearly.
    #                 Never make up an answer. If the question is not related to the context, politely respond that you are only able to answer questions that are related to the context."""
    #     )

    #     retriever = vector_store.as_retriever()
        
    #     qa = RetrievalQA.from_chain_type(
    #         llm=llm,
    #         chain_type="stuff",
    #         retriever=retriever,
    #         chain_type_kwargs={"prompt": prompt},
    #         input_key="question",
    #         output_key="answer",
    #     )

    #     print("RAG chain ready!")
    #     return qa