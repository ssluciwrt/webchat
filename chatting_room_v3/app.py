from flask import Flask, render_template
from flask_socketio import SocketIO, emit, send
from random import choice

app = Flask(__name__)
app.debug = True

wsocket = SocketIO(app)


userids = [i for i in range(1000)]
@app.route("/frame")
def frame():
    userid = choice(userids)
    return render_template("frame.html", userid=userid)

@wsocket.on("connect")
def connect(auth):
    userid = auth.get("userid")
    emit("message", {"msgtype": "notify", "userid": userid, "content": f"{userid} 上线了"}, broadcast=True)
    print(f"User:({userid}) Connected")

@wsocket.on("message")
def message(msg):
    emit("message", msg, broadcast=True)
    return "emitted"

@wsocket.on("disconnect")
def disconn():
    print("User Disconnected")


if __name__ == "__main__":
    wsocket.run(app, host="0.0.0.0")