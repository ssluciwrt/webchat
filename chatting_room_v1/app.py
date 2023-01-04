from flask import Flask, render_template, request, jsonify
from random import choice

app = Flask(__name__)

msgqueue = []
userids = [i for i in range(100)]

@app.route("/frame")
def frame():
    userid = choice(userids)
    userids.remove(userid)
    return render_template("frame.html", userid=userid)

@app.route("/txqueue", methods=["POST"])
def txqueue():
    userid = request.form.get("userid")
    msgcontent = request.form.get("msgcontent")
    msgqueue.append({"userid": userid, "msgcontent": msgcontent})
    print(msgqueue)
    return "Okay"

@app.route("/rcvqueue", methods=["POST"])
def rcvqueue():
    index = int(request.form.get("index"))
    data = {"msgpack": []}
    while index <= len(msgqueue) - 1:
        data["msgpack"].append(msgqueue[index])
        index += 1
    data.update({"index": index})
    return jsonify(data)


if __name__ == "__main__":
    app.run(debug=True)