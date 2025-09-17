from flask import Flask, request
import os

app = Flask(__name__)
UPLOAD_FOLDER = "photos"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return open("static/index.html").read()

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("photo")
    if file:
        path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(path)
        print(f"✅ Rasm saqlandi: {path}")
        return "OK"
    return "No file", 400

if __name__ == "__main__":
    import sys
    port = 8080
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    app.run(host="0.0.0.0", port=port)
