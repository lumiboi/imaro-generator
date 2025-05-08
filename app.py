from flask import Flask, render_template, request
from PIL import Image
import os
import uuid

app = Flask(__name__)
BASE = os.path.dirname(__file__)
REF_IMG = os.path.join(BASE, "static", "reference.png")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["image"]
        if file:
            filename = f"{uuid.uuid4().hex}.png"
            user_path = os.path.join(BASE, "static", "uploads", filename)
            file.save(user_path)

            ref = Image.open(REF_IMG).convert("RGBA").resize((512, 512))
            user = Image.open(user_path).convert("RGBA").resize((512, 512))

            blended = Image.blend(user, ref, alpha=0.4)

            result_path = os.path.join(BASE, "static", "results", filename)
            blended.save(result_path)

            return render_template("index.html", result_image=f"/static/results/{filename}")
    return render_template("index.html", result_image=None)

if __name__ == "__main__":
    os.makedirs("static/uploads", exist_ok=True)
    os.makedirs("static/results", exist_ok=True)

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
