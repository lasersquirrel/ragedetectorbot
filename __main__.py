import praw
from praw.exceptions import APIException
import json

username = "ragedetectorbot"
page = "https://github.com/lasersquirrel/ragedetectorbot"

reddit = praw.Reddit(username)

def sentiment_check(msg):
    """Sentiment checking stuff."""

    # Check sentiment
    # Have something like: end_msg = f"I am {sentiment*100}% sure that this is angry."

    end_msg = "" # Temporarily added to avoid pylint errors

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
        print(message.parent().title)
        # Different attribute names for comments and text posts
        try:
            og = message.parent().body
            check = sentiment_check(og)
        except AttributeError:
            try:
                og = message.parent().selftext
                check = sentiment_check(og)
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