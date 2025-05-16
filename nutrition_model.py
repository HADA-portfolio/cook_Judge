import os
import pandas as pd
import numpy as np
from PIL import Image
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow.keras import layers, models

# === 設定 ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_FOLDER = os.path.join(BASE_DIR, "data", "augmented_images", "images")

CSV_FILE = os.path.join(BASE_DIR, "data", "nutrition.csv")
MODEL_FILE = os.path.join(BASE_DIR, "data", "nutrition_model.keras")
IMAGE_SIZE = (32, 32)

# === データ読み込み ===
df = pd.read_csv(CSV_FILE)

X = []
y = []

for i, row in df.iterrows():
    img_path = os.path.join(IMAGE_FOLDER, row["filename"])
    try:
        img = Image.open(img_path).resize(IMAGE_SIZE).convert("RGB")
        X.append(np.array(img) / 255.0)
        y.append([row["calorie"], row["protein"], row["fat"], row["carbo"], row["salt"]])
    except Exception as e:
        print(f"画像読み込み失敗: {img_path}", e)

X = np.array(X)
y = np.array(y)

# === データ分割 ===
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# === モデル定義 ===
model = models.Sequential([
    layers.Input(shape=(32, 32, 3)),
    layers.Conv2D(32, (3, 3), activation='relu'),
    layers.MaxPooling2D(2),
    layers.Conv2D(64, (3, 3), activation='relu'),
    layers.MaxPooling2D(2),
    layers.Flatten(),
    layers.Dense(128, activation='relu'),
    layers.Dense(5)  # 出力は5つ（カロリー、たんぱく質、脂質、炭水化物、塩分）
])

model.compile(optimizer='adam', loss='mse', metrics=['mae'])

# === 学習 ===
model.fit(X_train, y_train, epochs=30, batch_size=16, validation_split=0.1)

# === 保存 ===
model.save(MODEL_FILE)
print(f"モデルを保存しました: {MODEL_FILE}")

import os
import pandas as pd
import numpy as np
from PIL import Image
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow.keras import layers, models

# === 設定 ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_FOLDER = os.path.join(BASE_DIR, "data", "augmented_images", "images")
CSV_FILE = os.path.join(BASE_DIR, "data", "nutrition.csv")
MODEL_FILE = os.path.join(BASE_DIR, "data", "nutrition_model.keras")
IMAGE_SIZE = (32, 32)

# === データ読み込み ===
df = pd.read_csv(CSV_FILE)

X = []
y = []

for i, row in df.iterrows():
    img_path = os.path.join(IMAGE_FOLDER, row["filename"])
    try:
        img = Image.open(img_path).resize(IMAGE_SIZE).convert("RGB")
        X.append(np.array(img) / 255.0)
        y.append([row["calorie"], row["protein"], row["fat"], row["carbo"], row["salt"]])
    except Exception as e:
        print(f"画像読み込み失敗: {img_path}", e)

X = np.array(X)
y = np.array(y)

# === データ分割 ===
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# === モデル定義（Dense層を1つ追加） ===
model = models.Sequential([
    layers.Input(shape=(32, 32, 3)),
    layers.Conv2D(32, (3, 3), activation='relu'),
    layers.MaxPooling2D(2),
    layers.Conv2D(64, (3, 3), activation='relu'),
    layers.MaxPooling2D(2),
    layers.Conv2D(128, (3, 3), activation='relu'),
    layers.MaxPooling2D(2),
    layers.Flatten(),
    layers.Dense(128, activation='relu'),     # 既存の全結合層
    layers.Dense(64, activation='relu'),      # ⭐️ 追加したDense層（強化ポイント！）
    layers.Dense(32, activation='relu'),      # ⭐️ 追加したDense層（強化ポイント！）
    layers.Dense(16, activation='relu'),      # ⭐️ 追加したDense層（強化ポイント！）
    layers.Dense(5)                            # 出力層（栄養素5つ）
])

# === コンパイル ===
model.compile(optimizer='adam', loss='mse', metrics=['mae'])

# === 学習 ===
model.fit(X_train, y_train, epochs=80, batch_size=4, validation_split=0.1)

# === テストデータで評価（精度の確認用）===
loss, mae = model.evaluate(X_test, y_test)
print(f"テストデータに対する損失（loss）: {loss:.2f}")
print(f"平均絶対誤差（MAE）: {mae:.2f}")

# === 保存 ===
model.save(MODEL_FILE)
print(f"モデルを保存しました: {MODEL_FILE}")
