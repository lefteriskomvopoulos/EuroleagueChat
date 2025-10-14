from flask import Flask, request, jsonify
from flask_cors import CORS
from main import questioning
from langchain.memory import ConversationBufferMemory

app = Flask(__name__)
CORS(app)

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

app = Flask(__name__)
CORS(app)
CORS(app, origins=["http://localhost:8000", "http://127.0.0.1:8000"])

def get_chatbot_response(user_message):

    print(f"Received message: {user_message}")

    return questioning(user_message)

@app.route("/chat", methods=["POST"])
def chat():

    try:
        data = request.get_json()
        user_message = data.get("message")

        if not user_message:
            return jsonify({"error": "No message provided"}), 400

        bot_response = get_chatbot_response(user_message)

        return jsonify({"reply": bot_response})

    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({"error": "An internal error occurred"}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)

