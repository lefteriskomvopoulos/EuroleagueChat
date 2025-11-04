from flask import Flask, request, jsonify, session
from flask_cors import CORS
from main import agent_executor
from langchain.memory import ConversationBufferMemory

app = Flask(__name__)
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

CORS(app, origins=["http://localhost:8000", "http://127.0.0.1:8000"])
app.secret_key = 'euroleague_chat'

# def get_chatbot_response(user_message):

#     print(f"Received message: {user_message}")

#     return questioning(user_message)

# @app.route("/chat", methods=["POST"])
# def chat():

#     try:
#         data = request.get_json()
#         user_message = data.get("message")

#         if not user_message:
#             return jsonify({"error": "No message provided"}), 400

#         bot_response = get_chatbot_response(user_message)

#         return jsonify({"reply": bot_response})

#     except Exception as e:
#         print(f"Error processing request: {e}")
#         return jsonify({"error": "An internal error occurred"}), 500

# if __name__ == "__main__":
#     app.run(debug=True, port=5000)


@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_message = data.get("message")

        if not user_message:
            return jsonify({"error": "No message provided"}), 400

        # 1. Load history from the user's session
        if 'chat_history' not in session:
            session['chat_history'] = []

        current_history = session['chat_history']

        if agent_executor is None:
             return jsonify({"error": "Agent not initialized"}), 500

        response = agent_executor.invoke({
            "input": user_message,
            "chat_history": current_history
        })
        
        bot_response = response['output']

        current_history.append(("human", user_message))
        current_history.append(("ai", bot_response))
        session['chat_history'] = current_history
        
        session.modified = True

        return jsonify({"reply": bot_response})

    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({"error": "An internal error occurred"}), 500

