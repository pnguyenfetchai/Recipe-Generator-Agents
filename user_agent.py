import json
import os
import sys
from flask import Flask, request
from fetchai import fetch
from fetchai.communication import (
    send_message_to_agent, parse_message_from_agent
)
from fetchai.crypto import Identity
from fetchai.registration import register_with_agentverse
from dotenv import load_dotenv

from uuid import uuid4

app = Flask(__name__)

load_dotenv(override=True)

AGENTVERSE_KEY = os.environ.get('AGENTVERSE_KEY', "")
if AGENTVERSE_KEY == "":
    sys.exit("Environment variable AGENTVERSE_KEY not defined")

@app.route('/register', methods=['GET'])
def register():
    ai_identity = Identity.from_seed("searching recipe eheheh", 0)

    name = "recipe-agent-search"

    # This is how you optimize your AI's search engine performance
    readme = """
        <description>This AI generates recipes based on ingredients</description>
        <use_cases>
            <use_case>Recipe generation from ingredients</use_case>
        </use_cases>
    """

    # The webhook that your AI receives messages on.
    ai_webhook = "http://127.0.0.1:5002/webhook"

    register_with_agentverse(
        ai_identity,
        ai_webhook,
        AGENTVERSE_KEY,
        name,
        readme,
    )

    return {"status": "Agent registered"}

@app.route('/search', methods=['GET'])
def search():
    query = "I want to generate a recipe"
    available_ais = fetch.ai(query)
    sender_identity = Identity.from_seed("whatever i want this to be, but i am searching", 0)

    # For the sake of example, the ingredients for the recipe request
    ingredients = ["tomato", "cheese", "basil", "olive oil"]

    for ai in available_ais.get('ais'):
        payload = {
            "ingredients": ingredients
        }

        other_addr = ai.get("address", "")

        print(f"sending a message to an ai, {other_addr}")

        send_message_to_agent(
            sender=sender_identity,
            target=ai.get("address", ""),
            payload=payload,
            session=uuid4()
        )

    return {"status": "Recipe agent searched"}

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print(f"webhook received: {data}")
    try:
        message = parse_message_from_agent(json.dumps(data))
    except ValueError as e:
        print(f"Error: {e}")
        return {"status": f"error: {e}"}

    sender = message.sender
    payload = message.payload

    # Handle the response from the recipe agent
    if "recipe" in payload:
        print(f"Recipe received: {payload['recipe']}")
        return {"status": "Recipe received and processed"}
    else:
        print("No recipe in the payload.")
        return {"status": "No recipe found"}

register()
search()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5002, debug=True)
