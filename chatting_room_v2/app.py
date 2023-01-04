from flask import Flask, render_template, request, jsonify
from queue import Queue
from random import choice

app = Flask(__name__)

quedict = {}
userids = [i for i in range(100)]

@app.route("/frame")
def frame():
    userid = choice(userids)
    quedict.update({userid: Queue()})
    return render_template("frame.html", userid=userid)

@app.route("/txqueue", methods=["POST"])
def txqueue():
    for que in quedict.values():
        que.put(dict(request.form))
    return "Qed"

@app.route("/rcvqueue", methods=["POST"])
def rcvqueue():
    userid = int(request.form.get("userid"))
    data = quedict[userid].get()
    print(data);
    return jsonify(data)



if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)