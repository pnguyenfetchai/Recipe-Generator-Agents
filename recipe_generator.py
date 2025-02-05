import json
from flask import Flask, request
from fetchai.communication import (
    send_message_to_agent, parse_message_from_agent
)
from fetchai.crypto import Identity
from fetchai.registration import register_with_agentverse
import os
import sys
from openai import OpenAI
from dotenv import load_dotenv
 


app = Flask(__name__)

load_dotenv(override=True)


AGENTVERSE_KEY = os.environ.get('AGENTVERSE_KEY')
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


client = OpenAI(api_key=OPENAI_API_KEY)

if AGENTVERSE_KEY == "":
    sys.exit("Environment variable AGENTVERSE_KEY not defined")

# You wouldn't normally want to expose the registration logic like this,
# but it works for a nice demo.
@app.route('/register', methods=['GET'])
def register():

    ai_identity = Identity.from_seed("I love this omgomgomgo ", 0)

    name = "recipe-agent"

    readme = """
        ![tag:innovation-lab](https://img.shields.io/badge/innovation--lab-3D8BD3)

        ![domain:cooking](https://img.shields.io/badge/cooking-3D8BD3)


        **Description**:  This AI Agent generates a recipe based on the ingredients you provide. It will create a simple and easy-to-follow recipe using the ingredients you input.

        **Input Data Model**
        ```
        class StockPriceRequest(Model):
            ticker: str
        ```

        **Output
        """
    
    # the address in which your agent will respond to incoming messages
    ai_webhook = os.environ.get('AGENT_WEBHOOK', "http://127.0.0.1:5003/webhook")

    register_with_agentverse(
        ai_identity,
        ai_webhook,
        AGENTVERSE_KEY,
        name,
        readme,
    )

    return {"status": "Agent registered"}

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json

    print("request received", data)
    try:
        message = parse_message_from_agent(json.dumps(data))
    except ValueError as e:
        return {"status": f"error: {e}"}

    sender = message.sender
    payload = message.payload
    ingredients = payload.get("ingredients", None)

    print(f"ingredients bro bro: {ingredients}")

    ai_identity = Identity.from_seed("I love this omgomgomgo ", 0)

    if sender == ai_identity.address:
        print("you are replying to yourself, just ignore.")
        return {"status": "Agent message processed"}

    if not ingredients:
        payload = {
            "err": "You need to provide ingredients in the message to get a recipe",
        }
    else:
        ingredients_list = ", ".join(ingredients)
        prompt = f"""
        You are a chef, and you will generate a recipe based on the following ingredients: {ingredients_list}.
        Please create a simple and easy-to-follow recipe using these ingredients.
        """
        
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        print(f"completion brother i love: {completion.choices[0].message.content}")
        
        payload = {
            "Response": completion.choices[0].message.content
        }

    send_message_to_agent(
        sender=ai_identity,
        target=sender,
        payload=payload,
        session=data["session"]
    )
    return {"status": "Agent message processed"}

register()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5003, debug=True)
