from flask import Flask, render_template, request, make_response, g
from redis import Redis
import os
import socket
import random
import json
import logging

option_a = os.getenv('OPTION_A', "Agree ah")
option_b = os.getenv('OPTION_B', "Disagree")
hostname = socket.gethostname()

app = Flask(__name__)

gunicorn_error_logger = logging.getLogger('gunicorn.error')
app.logger.handlers.extend(gunicorn_error_logger.handlers)
app.logger.setLevel(logging.INFO)

# Load tweets from a simple text file.
# Each line in the file is treated as a separate tweet.
try:
    with open('tweets.txt', 'r') as f:
        tweets = [line.strip() for line in f.readlines()]
except FileNotFoundError:
    app.logger.warning("tweets.txt not found. ")
    tweets = ["Could not find tweets.txt. "]


def get_redis():
    if not hasattr(g, 'redis'):
        g.redis = Redis(host="redis", db=0, socket_timeout=5)
    return g.redis


@app.route("/", methods=['POST', 'GET'])
def hello():
    voter_id = request.cookies.get('voter_id')
    if not voter_id:
        voter_id = hex(random.getrandbits(64))[2:-1]

    vote = None

    if request.method == 'POST':
        redis = get_redis()
        vote = request.form['vote']
        app.logger.info('Received vote for %s', vote)
        data = json.dumps({'voter_id': voter_id, 'vote': vote})
        redis.rpush('votes', data)

    # Select a random tweet (a single line of text) from the loaded list
    tweet = random.choice(tweets) if tweets else ""

    resp = make_response(render_template(
        'index.html',
        option_a=option_a,
        option_b=option_b,
        hostname=hostname,
        vote=vote,
        tweet=tweet,  # Pass the selected tweet string to the template
    ))
    resp.set_cookie('voter_id', voter_id)
    return resp


if __name__ == "__main__":
    # Make sure to create a 'tweets.txt' file in the same directory
    app.run(host='0.0.0.0', port=80, debug=True, threaded=True)

