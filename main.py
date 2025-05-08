import os
from flask import Flask, render_template, request
from deepface import DeepFace
import requests
from PIL import Image
import cv2
import numpy as np
import io
import base64

app = Flask(__name__)

# Sabit fotoğraf URL'si
FIXED_IMAGE_URL = "https://i.hizliresim.com/p5s5as7.png"

# X API'den profil fotoğrafı alma
def get_profile_picture(username):
    api_key = os.getenv("X_API_KEY", "YOUR_API_KEY")
    response = requests.get(
        f"https://api.x.com/users/{username}/profile_image",
        headers={"Authorization": f"Bearer {api_key}"}
    )
    if response.status_code != 200:
        return None
    return response.content

# Görüntüyü dosyaya kaydetme
def save_image(data, path):
    img = Image.open(io.BytesIO(data))
    img.save(path)

# Görüntüyü base64'e çevirme
def image_to_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

# Ana sayfa
@app.route('/')
def index():
    return render_template('index.html')

# Fotoğraf harmanlama
@app.route('/generate', methods=['POST'])
def generate():
    username = request.form.get('username')
    if not username:
        return render_template('index.html', error="Kullanıcı adı gerekli")

    # Profil fotoğrafını al
    profile_pic_data = get_profile_picture(username)
    if not profile_pic_data:
        return render_template('index.html', error="Kullanıcı bulunamadı veya profil fotoğrafı yok")

    # Geçici dosyalar için yollar
    profile_pic_path = f"temp_{username}.png"
    fixed_image_path = "fixed_image.png"
    result_path = f"result_{username}.png"

    try:
        # Profil fotoğrafını kaydet
        save_image(profile_pic_data, profile_pic_path)
        # Sabit fotoğrafı indir ve kaydet
        save_image(requests.get(FIXED_IMAGE_URL, stream=True).raw.read(), fixed_image_path)

        # DeepFace ile yüz analizi
        DeepFace.verify(
            img1_path=fixed_image_path,
            img2_path=profile_pic_path,
            model_name="Facenet",
            enforce_detection=False  # Yüz algılama başarısız olursa hata vermesin
        )

        # Görüntüleri harmanla (basit bir blending)
        img1 = cv2.imread(fixed_image_path)
        img2 = cv2.imread(profile_pic_path)
        if img1.shape != img2.shape:
            img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
        blended = cv2.addWeighted(img1, 0.5, img2, 0.5, 0.0)
        cv2.imwrite(result_path, blended)

        # Sonucu base64'e çevir
        result_base64 = image_to_base64(result_path)

        # Geçici dosyaları sil
        for path in [profile_pic_path, fixed_image_path, result_path]:
            if os.path.exists(path):
                os.remove(path)

        return render_template('index.html', image=f"data:image/png;base64,{result_base64}")

    except Exception as e:
        # Hata durumunda dosyaları sil
        for path in [profile_pic_path, fixed_image_path, result_path]:
            if os.path.exists(path):
                os.remove(path)
        return render_template('index.html', error=f"Hata oluştu: {str(e)}")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.getenv("PORT", 5000)))