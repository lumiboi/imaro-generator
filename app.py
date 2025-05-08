import os
from flask import Flask, render_template, request
from PIL import Image
import tensorflow as tf
import uuid
import numpy as np

app = Flask(__name__)

# Modeli yükle (bu model önceden eğitilmiş olmalı)
model = tf.keras.applications.MobileNetV2(weights='imagenet', input_shape=(224, 224, 3))

BASE = os.path.dirname(__file__)
REF_IMG = os.path.join(BASE, "static", "reference.png")

# Fotoğraf işleme ve yapay zeka ile harmanlama fonksiyonu
def blend_images(user_image_path):
    # Fotoğrafı aç
    user_img = Image.open(user_image_path).convert("RGB")
    user_img = user_img.resize((224, 224))  # Model için boyutlandırma
    user_img_array = np.array(user_img) / 255.0

    # Modeli kullanarak tahmin yap
    img_array = np.expand_dims(user_img_array, axis=0)
    predictions = model.predict(img_array)

    # Burada modelden alınan çıktıyı işleyebiliriz (örneğin, sınıflandırma veya stil transferi)
    # Bu örnekte sadece görselin üzerine bir işlem yapılacak, sonuç olarak daha farklı işlemler yapılabilir.

    return user_img

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["image"]
        if file:
            filename = f"{uuid.uuid4().hex}.png"
            user_path = os.path.join(BASE, "static", "uploads", filename)
            file.save(user_path)

            # Harmanlama işlemini yap
            blended_image = blend_images(user_path)

            # Harmanlanmış fotoğrafı kaydet
            result_path = os.path.join(BASE, "static", "results", filename)
            blended_image.save(result_path)

            return render_template("index.html", result_image=f"/static/results/{filename}")

    return render_template("index.html", result_image=None)

if __name__ == "__main__":
    os.makedirs("static/uploads", exist_ok=True)
    os.makedirs("static/results", exist_ok=True)

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
