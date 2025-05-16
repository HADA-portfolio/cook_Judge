import os
from flask import Flask, request, redirect, send_from_directory
import numpy as np
from keras import models
from PIL import Image
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "data", "uploads")
MODEL_FILE = os.path.join(BASE_DIR, "data", "nutrition_model.keras")
CSV_FILE = os.path.join(BASE_DIR, "data", "nutrition.csv")  # 栄養データCSV

# 栄養ラベル
LABELS = ["カロリー(kcal)", "たんぱく質(g)", "脂質(g)", "炭水化物(g)", "食塩相当量(g)"]
CSS_URL = "https://cdn.jsdelivr.net/npm/bulma@1.0.2/css/bulma.min.css"
HTML_HEADER = f"""
<!DOCTYPE html><html>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="{CSS_URL}"><body>
<section class="hero has-background-info"><div class="hero-body">
    <h1 class="title">料理画像から栄養を予測</h1></div></section>
"""

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

model = models.load_model(MODEL_FILE)
df = pd.read_csv(CSV_FILE)

@app.route("/")
def root():
    return f"""{HTML_HEADER}
    <div class="box file">
        <form method="post" action="/predict" enctype="multipart/form-data">
            <input type="file" name="file" class="file-label" /><br>
            <input type="submit" value="栄養予測を実行" class="button is-primary" />
        </form></div></body></html>
    """

@app.route("/predict", methods=["POST"])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']
    if not (file and file.filename.endswith(('.jpg', '.jpeg'))):
        return f"""{HTML_HEADER}<h1>画像ファイルをアップロードしてください</h1></body></html>"""

    filename = file.filename
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    try:
        img = Image.open(file_path).resize((32, 32)).convert("RGB")
        X = np.array([np.array(img) / 255.0])
    except Exception as e:
        return f"""{HTML_HEADER}<h1>画像の読み込みに失敗しました</h1></body></html>"""

    # 予測実行
    pred = model.predict([X])[0]

    # 実際の値（同じ画像名がnutrition.csvにある前提）
    actual_row = df[df['filename'] == filename]
    if not actual_row.empty:
        actual = actual_row.iloc[0][["calorie", "protein", "fat", "carbo", "salt"]].values
        diff = np.abs(pred - actual)
        result_table = "".join([
            f"<tr><td>{label}</td><td>{p:.1f}</td><td>{a:.1f}</td><td>{d:.1f}</td></tr>"
            for label, p, a, d in zip(LABELS, pred, actual, diff)
        ])
        table_header = "<thead><tr><th>項目</th><th>予測値</th><th>実際の値</th><th>誤差</th></tr></thead>"
    else:
        result_table = "".join([
            f"<tr><td>{label}</td><td>{value:.1f}</td></tr>"
            for label, value in zip(LABELS, pred)
        ])
        table_header = "<thead><tr><th>項目</th><th>予測値</th></tr></thead>"

    return f"""{HTML_HEADER}
    <div class="card" style="font-size:1.2em; padding:1em;">
        <h2 class="title is-4">予測結果</h2>
        <table class="table is-striped">
            {table_header}
            <tbody>{result_table}</tbody>
        </table>
        <img src="/uploads/{filename}" width="300"><br>
        <a href="/" class="button mt-4">別の画像を試す</a>
    </div></body></html>
    """

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
