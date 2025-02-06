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
      
        ![tag:innovation-lab](https://img.shields.io/badge/innovation--lab-3D8BD3)

        ![domain:cooking](https://img.shields.io/badge/cooking-3D8BD3)


        **Description**:  user agent that sends a message to the recipe agent to generate a recipe based on the ingredients you provide. 
        **Input Data Model**
        ```
        class Ingridients(Model):
            ingredients: list[str]
        ```

        **Output**


        
    """

    ai_webhook = "http://127.0.0.1:5002/webhook"

    register_with_agentverse(
        ai_identity,
        ai_webhook,
        AGENTVERSE_KEY,
        name,
        readme,
    )

    return {"status": "Agent registered"}

@app.route('/generate', methods=['GET'])
def generate():
    sender_identity = Identity.from_seed("searching recipe eheheh", 0)

    ingredients = ["tomato", "cheese", "basil", "olive oil"]

    target_address = "agent1qth28h5gqjn9m4jrhhrx6qqdrugj0dvdqq4pu3httmncqu69pjjsc9xat24"

    payload = {
        "ingredients": ingredients
    }

    send_message_to_agent(
        sender=sender_identity,
        target=target_address,
        payload=payload,
        session=uuid4()
    )

    return {"status": "Message sent to agent"}
  
    

@app.route('/webhook', methods=['POST'])
def webhook():
    
    data = request.json
    print("this is the dataaaa", data)
  
    try:
        message = parse_message_from_agent(json.dumps(data))
    except ValueError as e:
        print(f"Error: {e}")
        return {"status": f"error: {e}"}

    # sender = message.sender
    payload = message.payload

    recipe_text = payload.get("Response", "")

    print("Recipe generated:\n", recipe_text)

    return {"status": "yipeee we got a response!"}

register()
    



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5002, debug=True)
