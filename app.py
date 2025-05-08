import os
import requests
from flask import Flask, render_template, request, send_file
from PIL import Image
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image as keras_image
from io import BytesIO

app = Flask(__name__)

# Profil fotoğrafını URL'den alma
def get_twitter_profile_picture(username):
    # Twitter profil fotoğrafının URL formatını kullan
    return f"https://pbs.twimg.com/profile_images/{username}/profile_image.jpg"

# Stil Transferi Fonksiyonu
def style_transfer(content_image_path, style_image_path):
    # Stil transferi için TensorFlow kullanımı
    content_image = keras_image.load_img(content_image_path)
    style_image = keras_image.load_img(style_image_path)

    # Resimleri tensor formatına çevir
    content_image = tf.image.convert_image_dtype(np.array(content_image), dtype=tf.float32)
    style_image = tf.image.convert_image_dtype(np.array(style_image), dtype=tf.float32)

    # Görüntüleri yeniden boyutlandır (işlem için uygun boyutta)
    content_image = tf.image.resize(content_image, (512, 512))
    style_image = tf.image.resize(style_image, (512, 512))

    # Modeli yükle ve stil transferini gerçekleştir
    model = tf.saved_model.load("style_transfer_model")

    stylized_image = model(content_image, style_image)

    # Sonucu bellek üzerinde tutmak için BytesIO kullanıyoruz
    img = Image.fromarray(np.uint8(stylized_image.numpy()))
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)  # Başlangıca getir
    return img_byte_arr

# Ana sayfa
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form['username']
        profile_image_url = get_twitter_profile_picture(username)

        # Kullanıcı profil fotoğrafını indir
        response = requests.get(profile_image_url)
        if response.status_code == 200:
            with open('user_image.jpg', 'wb') as file:
                file.write(response.content)

            # Stil transferini yap ve sonucu belleğe al
            img_byte_arr = style_transfer('user_image.jpg', 'style_image.jpg')

            # Çıktıyı tarayıcıya gönder
            return send_file(img_byte_arr, mimetype='image/png')

        else:
            error_message = "Profil fotoğrafı bulunamadı! Lütfen geçerli bir kullanıcı adı girin."
            return render_template('index.html', error_message=error_message)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
