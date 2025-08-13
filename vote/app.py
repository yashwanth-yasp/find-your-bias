import json
import logging
import os
import random
import socket

from flask import Flask, g, make_response, render_template, request
from redis import Redis

# Configuration from environment variables or defaults
option_a = os.getenv("OPTION_A", "Agree ah")
option_b = os.getenv("OPTION_B", "Disagree")
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

    vote = None

    # Process POST requests (votes)
    if request.method == "POST":
        redis = get_redis()
        vote = request.form["vote"]
        app.logger.info("vote for %s from voter_id: %s", vote, voter_id)
        data = json.dumps({"voter_id": voter_id, "vote": vote})
        redis.rpush("votes", data)  # Push vote data to Redis list

    # Select a random tweet (a single line of text) from the loaded list
    tweet = random.choice(tweets) if tweets else ""

    # Prepare the response and set the voter_id cookie
    resp = make_response(
        render_template(
            "index.html",
            option_a=option_a,
            option_b=option_b,
            hostname=hostname,
            vote=vote,
            tweet=tweet,  # Pass the selected tweet string to the template
        )
    )
    resp.set_cookie("voter_id", voter_id)
    return resp


if __name__ == "__main__":
    # Ensure 'tweets.txt' exists in the same directory for tweets to load.
    # This block is for local development runs, not for production Gunicorn.
    app.run(host="0.0.0.0", port=80, debug=True, threaded=True)

