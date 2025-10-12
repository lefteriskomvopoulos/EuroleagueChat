from flask import Flask, request, jsonify
from flask_cors import CORS

from main import questioning

# 1. Initialize Flask App and CORS
app = Flask(__name__)
# This allows your frontend to make requests to this backend
CORS(app) 

# =================================================================
# 2. LOAD YOUR CHATBOT MODEL/LOGIC HERE
#    - This part is specific to your project.
#    - For example, you might load a machine learning model,
#      initialize a class, or connect to a service.
# =================================================================
def get_chatbot_response(user_message):
    """
    This is a placeholder function.
    Replace this with a call to your actual chatbot logic.
    """
    print(f"Received message: {user_message}")
    # --- YOUR CHATBOT LOGIC GOES HERE ---
    # Example: response = my_chatbot.get_reply(user_message)
    response = f"This is my reply to: '{questioning(user_message)}'"
    # ------------------------------------
    return response

# 3. Define the API endpoint
@app.route("/chat", methods=["POST"])
def chat():
    """
    This function is called when the frontend sends a message.
    """
    try:
        data = request.get_json()
        user_message = data.get("message")

        if not user_message:
            return jsonify({"error": "No message provided"}), 400

        # 4. Get the response from your chatbot
        bot_response = get_chatbot_response(user_message)

        # 5. Send the response back to the frontend
        return jsonify({"reply": bot_response})

    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({"error": "An internal error occurred"}), 500

# This is for local testing
if __name__ == "__main__":
    app.run(debug=True, port=5000)
