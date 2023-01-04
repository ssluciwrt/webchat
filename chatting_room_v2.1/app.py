from flask import Flask, render_template, request, json
from redis import Redis
from random import choice

app = Flask(__name__)
redisconn = Redis("127.0.0.1", 6379, 0, decode_responses=True)
userids = [i for i in range(1000)]


@app.route("/frame")
def frame():
    userid = choice(userids)
    return render_template("/frame.html", userid=userid)

@app.route("/submsg", methods=["POST"])
def submsg():
    pubsub = redisconn.pubsub(ignore_subscribe_messages=True)
    pubsub.subscribe("chatting")
    msg = pubsub.listen()
    return next(msg).get("data")

@app.route("/pubmsg", methods=["POST"])
def pubmsg():
    msg = json.dumps(dict(request.form))
    redisconn.publish("chatting", msg)
    return "pubbed"



if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)