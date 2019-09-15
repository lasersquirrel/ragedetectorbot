import praw
from praw.exceptions import APIException
import json
import joblib
from keras.models import model_from_json


username = "ragedetectorbot"
page = "https://github.com/lasersquirrel/ragedetectorbot"

### LOAD IN REQUIRED FILES FOR CYBER AGGRESSION DETECTIOn
cyber_tokenizer = joblib.load("./model/cyber_tokenizer.joblib")
json_file = open("./model/cyber_model.json")
model_json = json_file.read()
json_file.close()
cyber_model = model_from_json(model_json)
cyber_model.load_weights("./model/cyber_model.h5")
cyber_model._make_predict_function()

reddit = praw.Reddit(username)

def sentiment_check(msg):
    """Sentiment checking stuff."""
    tokenized_msg = cyber_tokenizer.texts_to_matrix([msg])
    cyber_prediction  = cyber_model.predict_proba(tokenized_msg)
    short_agro_value = int(cyber_prediction[0][1]*100)

    if short_agro_value > 59:
        end_msg = f"Rage bot says you need to slow your roll bro... (Rage Level: {short_agro_value}%)"
    elif short_agro_value < 41:
        end_msg = f"Rage bot says nice chilling bro... (Rage Level: {short_agro_value}%)"
    else:
        end_msg = f"Rage bot could not assess rage level. (Rage Level: {short_agro_value}%)"

    footer = f"  \n\n^(Bleep bloop, I'm a bot! Mention me to check sentiment on comments/posts. |)  [^(GitHub page)]({page})"
    end_msg += footer
    return end_msg

# Open the log file
f = open("log.txt", "r")
lines = f.readlines()
log = "".join(lines)
log = log.replace("\r", "").replace("\n", "")
log = json.loads(log)
f.close()

# Main thing
for message in reddit.inbox.stream():
    # Check if it's a mention
    if "u/"+username in message.body:
        # Different attribute names for comments and text posts
        try:
            og = message.parent().body
            check = sentiment_check(og)
        except AttributeError:
            try:
                og = message.parent().selftext
                if og != "":
                    check = sentiment_check(og)
                else:
                    raise AttributeError("Continue")
            except AttributeError:
                try:
                    og = message.parent().title
                    check = sentiment_check(og)
                except AttributeError:
                    check = None
                    print(f"Failed to translate {message.parent()}.")
        
        # Make sure that the bot could actually analyse the message
        if check is not None:
            try:
                print(f"Ran Analysis on ID {message.parent()}: {check}")
                reply = message.reply(check)
                # Simulate Reddit auto-upvote
                reply.upvote()
                message.mark_read()
                # Add the message to the log
                # Stored as dict; PARENT_ID: [og_content, check, summoner]
                log[message.parent().id] = [og, check, message.author.name]
                f = open("log.txt", "w")
                f.writelines(json.dumps(log))
                f.close()
            except APIException:
                print("Could not send message.")