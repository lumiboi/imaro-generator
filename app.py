import os
from flask import Flask, request, render_template, send_file
from PIL import Image, ImageDraw, ImageFont
from werkzeug.utils import secure_filename
import uuid

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
GENERATED_FOLDER = 'static/generated'
BASE_IMAGE_PATH = 'static/base_imaro.png'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(GENERATED_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    twitter_handle = request.form['twitter_handle']
    file = request.files['user_image']

    if file and twitter_handle:
        filename = secure_filename(file.filename)
        user_image_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(user_image_path)

        # Sabit ve kullanıcı görselini birleştir
        base_img = Image.open(BASE_IMAGE_PATH).convert("RGBA")
        user_img = Image.open(user_image_path).resize((256, 256)).convert("RGBA")
        base_img.paste(user_img, (50, 50), user_img)

        # Twitter kullanıcı adını yaz
        draw = ImageDraw.Draw(base_img)
        try:
            font = ImageFont.truetype("arial.ttf", 40)
        except:
            font = ImageFont.load_default()
        draw.text((50, 320), f"@{twitter_handle}", fill="white", font=font)

        output_path = os.path.join(GENERATED_FOLDER, f"{uuid.uuid4()}.png")
        base_img.save(output_path)

        return send_file(output_path, mimetype='image/png')

    return "Lütfen kullanıcı adı ve görsel sağlayın."

if __name__ == '__main__':
    app.run(debug=True)
