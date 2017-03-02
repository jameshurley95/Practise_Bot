import os
import sys
import json
import random    # this will be used for the factbot, note to self, if it crashes get rid of this
import linecache
import time


import requests
from flask import Flask, request

app = Flask(__name__)


@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello world", 200


@app.route('/', methods=['POST'])
def webhook():

    # endpoint for processing incoming messaging events

    data = request.get_json()
    log(data)  # you may not want to log every incoming message in production, but it's good for testing

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):  # someone sent us a message

                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    message_text = messaging_event["message"]["text"]  # the message's text
                    
                    m = message_text.lower()   # make sure all text inputs for checking are in lowercase otherwise it will not understand!
                    
                    fact_line_number = random.randint(1,103)   #Creates a random number for how many facts I have saved, I want 2000 facts.
                    
                    random_response_to_amazement = random.randint(1,4)
                    
                    random_response_line_number = random.randint(1,7)
                    
                    greeting_line_number = random.randint(1,23)
                   
                    if "hello" in m or "hi" in m or "whats up" in m:
                        send_message(sender_id,linecache.getline('Dondie_greatings.txt', greeting_line_number))
                    elif "bye" in m or "seeyou" in m or "goodbye" in m:
                        send_message(sender_id,"bye Dondie! Hope you have lovely rest of day")
                    elif "fact" in m:
                        send_message(sender_id,linecache.getline('FactBot_Facts.txt', fact_line_number))
                        send_message(sender_id,linecache.getline('Comments_for_each_fact.txt', fact_line_number))
                    elif "f" in m:
                        send_message(sender_id,fact_to_post)
                    elif "nice" in m or "cool" in m or "interesting" in m or "wow" in m or "amazing" in m:
                        send_message(sender_id,linecache.getline('responses_to_amazement.txt', random_response_to_amazement))
                    elif "meow" in m:
                        send_message(sender_id,"https://www.youtube.com/watch?v=MEcwclDZq6U")
                        send_message(sender_id,"enjoy the cute cuddly cats :)")
                    elif "it is going okay" in m or "i guess" in m:
                        send_message(sender_id,"Everything will be fine, just focus on working now and don't be intimidated by the future")
                    elif "how are you" in m:
                        send_message(sender_id,"I am good thankyou, how is work going?")
                    else:
                        send_message(sender_id,linecache.getline('random_responses_when_input_not_understood.txt', random_response_line_number))

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    pass

    return "ok", 200




def send_message(recipient_id, message_text):

    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


def log(message):  # simple wrapper for logging to stdout on heroku
    print str(message)
    sys.stdout.flush()


if __name__ == '__main__':
    app.run(debug=True)
