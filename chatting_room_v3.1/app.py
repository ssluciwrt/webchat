from flask import Flask, render_template, request, session, redirect, url_for, flash, json
from flask_socketio import SocketIO, emit, send
from redis import Redis
import time 

app = Flask(__name__)
app.secret_key = "dev"
app.debug = True
iosvr = SocketIO(app)
redisconn = Redis("127.0.0.1", 6379, 0, decode_responses=True)

@app.before_request
def session_auth():
    if request.path == "/gohome":
        return
    if "chatter" not in session:
        return redirect(url_for("gohome"))


@app.route("/gohome", methods=["GET", "POST"])
def gohome():
    if request.method == "POST":
        chatter = request.form.get("chatter")
        if not chatter.strip():
            flash("提示: 先留个名")
            return redirect(url_for("gohome"))
        session["chatter"] = chatter
        return redirect(url_for("frame"))
    return render_template("/reg.html")

@app.route("/frame")
def frame():
    chatter = session.get("chatter")
    return render_template("frame.html", chatter=chatter)

@iosvr.on("connect")
def connect_handler():
    remote = request.environ.get("REMOTE_ADDR")
    chatter = session.get("chatter")
    redisconn.hset("status", chatter, 1) # change the status of the chatter themself just connected
    chatterstatus = redisconn.hgetall("status") # obtain the status of all chatters from redisz
    emit("status", chatterstatus) # obtain the status of all chatters through socket
    emit("status", {chatter: 1}, broadcast=True, include_self=False) # broadcast my status to others
    msglist = redisconn.lrange("messages", 0, 19) # fetch history message for frontend loading
    if msglist:
        session["histindex"] = 20 # control history message index
        msglist.reverse()
        for eachmsg in msglist:
            emit("message", json.loads(eachmsg))
    print(f"{remote} - [{time.strftime('%Y/%m/%d %H:%M:%S')}] \"A User Connected - UserID: {chatter}\"")

@iosvr.on("message")
def msg_handler(msg):
    msg["time"] = time.time()
    redisconn.lpush("messages", json.dumps(msg))
    send(msg, broadcast=True, include_self=False)
    return "sent"

@iosvr.on("history")
def history_handler():
    start = session.get("histindex")
    end = start + 5
    msglist = redisconn.lrange("messages", start, end)
    if msglist:
        session["histindex"] = end + 1
        for eachmsg in msglist:
            emit("history", json.loads(eachmsg))
    else:
        emit("history", 0)


@iosvr.on("typing")
def typing_handler(msg):
    emit("typing", msg, broadcast=True, include_self=False)

@iosvr.on("disconnect")
def disconn_handler():
    remote = request.environ.get("REMOTE_ADDR")
    chatter = session.get("chatter")
    redisconn.hset("status", chatter, 0) # change my status in redis
    emit("status", {chatter: 0}, broadcast=True, include_self=False) # broadcast my status to others
    print(f"{remote} - [{time.strftime('%Y/%m/%d %H:%M:%S')}] \"A User Disconnected - UserID: {chatter}\"")


@app.route("/goout")
def goout():
    session.pop("chatter")
    return redirect(url_for("gohome"))

if __name__ == "__main__":
    iosvr.run(app, host="0.0.0.0")