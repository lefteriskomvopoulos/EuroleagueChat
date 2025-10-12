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