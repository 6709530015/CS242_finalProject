from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

# หน้าแรก (HTML Template)
@app.route("/")
def home():
    return render_template("index.html")

# API JSON ตัวอย่าง
@app.route("/api/greet/<name>")
def greet(name):
    return jsonify({"message": f"Hello, {name}!"})

# รับข้อมูลจากฟอร์ม POST
@app.route("/api/echo", methods=["POST"])
def echo():
    data = request.json  # รับ JSON
    return jsonify({"you_sent": data})

if __name__ == "__main__":
    app.run(debug=True)