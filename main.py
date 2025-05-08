from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
from deepface import DeepFace
from PIL import Image
import io
import base64
import numpy as np
import cv2
import os

app = FastAPI()

# Sabit fotoğraf URL'si
FIXED_IMAGE_URL = "https://i.hizliresim.com/p5s5as7.png"

# X API'den profil fotoğrafı alma (Basitleştirilmiş)
def get_profile_picture(username: str) -> str:
    # Gerçek X API entegrasyonu için: https://x.ai/api
    # Örnek olarak içerik döndürüyoruz, gerçekte API çağrısı yapılacak
    response = requests.get(f"https://api.x.com/users/{username}/profile_image", headers={"Authorization": "Bearer YOUR_API_KEY"})
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Kullanıcı bulunamadı veya profil fotoğrafı yok")
    return response.content

# Görüntüyü dosyaya kaydetme
def save_image_from_url(url: str, path: str):
    img = Image.open(requests.get(url, stream=True).raw)
    img.save(path)

# Görüntüyü base64'e çevirme
def image_to_base64(image_path: str) -> str:
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

class UsernameRequest(BaseModel):
    username: str

@app.post("/generate")
async def generate(request: UsernameRequest):
    username = request.username
    if not username:
        raise HTTPException(status_code=400, detail="Kullanıcı adı gerekli")

    # Profil fotoğrafını indir
    profile_pic_path = f"temp_{username}.png"
    try:
        profile_pic_content = get_profile_picture(username)
        with open(profile_pic_path, "wb") as f:
            f.write(profile_pic_content)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Sabit fotoğrafı indir
    fixed_image_path = "fixed_image.png"
    save_image_from_url(FIXED_IMAGE_URL, fixed_image_path)

    # DeepFace ile yüz manipülasyonu
    try:
        # Yüz özelliklerini analiz et
        result = DeepFace.verify(img1_path=fixed_image_path, img2_path=profile_pic_path, model_name="Facenet")
        # Basit harmanlama (geliştirilebilir)
        img1 = cv2.imread(fixed_image_path)
        img2 = cv2.imread(profile_pic_path)
        blended = cv2.addWeighted(img1, 0.5, img2, 0.5, 0.0)
        result_path = f"result_{username}.png"
        cv2.imwrite(result_path, blended)

        # Sonucu base64'e çevir
        result_base64 = image_to_base64(result_path)

        # Geçici dosyaları sil
        os.remove(profile_pic_path)
        os.remove(result_path)
        if os.path.exists(fixed_image_path):
            os.remove(fixed_image_path)

        return {"image": f"data:image/png;base64,{result_base64}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Yüz manipülasyonu başarısız: {str(e)}")

# Statik dosyaları sunmak için
from fastapi.staticfiles import StaticFiles
app.mount("/static", StaticFiles(directory="static"), name="static")