import json
import logging
import os
import random
import socket
import uuid

from flask import Flask, g, make_response, render_template, request, redirect, url_for
from redis import Redis

# Configuration from environment variables or defaults
option_a = os.getenv("OPTION_A", "Agree boooo")
option_b = os.getenv("OPTION_B", "Disagree change")
hostname = socket.gethostname()

app = Flask(__name__)

# Configure logging to use Gunicorn's logger
gunicorn_error_logger = logging.getLogger("gunicorn.error")
app.logger.handlers.extend(gunicorn_error_logger.handlers)
app.logger.setLevel(logging.INFO)

# Load tweets from a simple text file.
# Each line in the file is treated as a separate tweet.
try:
    with open("tweets.txt", "r") as f:
        tweets = [line.strip() for line in f.readlines()]
except FileNotFoundError:
    app.logger.warning(
        "tweets.txt not found."
    )
    tweets = ["Could not find tweets.txt."]


def get_redis():
    """
    Establishes and returns a Redis connection, reusing it if already available
    in the application context.
    """
    if not hasattr(g, "redis"):
        g.redis = Redis(host="redis", db=0, socket_timeout=5)
    return g.redis


@app.route("/", methods=["POST", "GET"])
def hello():
    """
    Handles voting logic and renders the main page.
    Generates a voter_id if not present in cookies, processes votes,
    and displays a random tweet.
    """
    # Get or create voter ID from cookies
    voter_id = request.cookies.get("voter_id")
    if not voter_id:
        voter_id = hex(random.getrandbits(64))[2:-1]

    # Handle room creation
    if 'new_room' in request.args:
        room_id = str(uuid.uuid4())
        return redirect(url_for('hello', room_id=room_id))

    room_id = request.args.get('room_id')
    if not room_id:
        # Default to a new room if none is specified
        return redirect(url_for('hello', new_room='true'))


    # Get a random tweet for the user to vote on.
    # The tweet is stored in a hidden form field to be submitted with the vote.
    tweet = random.choice(tweets)

    # Process POST requests (votes)
    if request.method == "POST":
        redis = get_redis()
        vote = request.form["vote"]
        room_id = request.form["room_id"]
        tweet = request.form["tweet"]
        app.logger.info(f"Received vote for '{vote}' in room '{room_id}' for tweet: '{tweet}'")
        data = json.dumps({"voter_id": voter_id, "vote": vote, "tweet": tweet, "room_id": room_id})
        redis.rpush("votes", data)  # Push vote data to Redis list

    # Prepare the response and set the voter_id cookie
    resp = make_response(render_template(
        "index.html",
        option_a=option_a,
        option_b=option_b,
        hostname=hostname,
        tweet=tweet,
        room_id=room_id,
    ))
    resp.set_cookie("voter_id", voter_id)
    return resp


if __name__ == "__main__":
    # Ensure 'tweets.txt' exists in the same directory for tweets to load.
    # This block is for local development runs, not for production Gunicorn.
    app.run(host="0.0.0.0", port=80, debug=True, threaded=True)
