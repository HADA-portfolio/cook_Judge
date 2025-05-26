#料理画像を読み込み、学習モデルを作成するコード

#ライブラリのインポート
import os
import pandas as pd
import numpy as np
from PIL import Image
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow.keras import layers, models

# ベースフォルダを取得
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
#学習に使う画像のフォルダを指定
IMAGE_FOLDER = os.path.join(BASE_DIR, "data", "augmented_images", "images")
#栄養情報のCSVファイルの場所を指定
CSV_FILE = os.path.join(BASE_DIR, "data", "nutrition.csv")
#学習モデルを保存する場所を指定
MODEL_FILE = os.path.join(BASE_DIR, "data", "nutrition_model.keras")
#画像のサイズを指定
IMAGE_SIZE = (128, 128)

#CSV_FILEを読み込む
df = pd.read_csv(CSV_FILE)

X = [] #画像データ（入力)を入れるためのリスト
y = [] #栄養データ（正解ラベル）を入れるためのリスト

for i, row in df.iterrows(): #CSV_FILEからデータを取り出し、番号と各データを変数に格納
    img_path = os.path.join(IMAGE_FOLDER, row["filename"]) #画像フォルダ名と画像ファイル名をつなぎ、画像ファイルのパスを作成
    #以下を実行する
    try:
        img = Image.open(img_path).resize(IMAGE_SIZE).convert("RGB") #画像を開いて、サイズを32×32にし、色をRGBに変える
        X.append(np.array(img) / 255.0) #画像を数値の配列に変換、255で割って0〜1の範囲に正規化し、Xに追加
        y.append([row["calorie"], row["protein"], row["fat"], row["carbo"], row["salt"]]) #5つの栄養素の数値（カロリー・たんぱく質・脂質・炭水化物・塩分）を yに追加
    #エラーの場合、以下を実行する
    except Exception as e:
        print(f"画像読み込み失敗: {img_path}", e) #画像読み込みの旨メッセージ

#NumPy配列に変換
X = np.array(X)
y = np.array(y)

#学習用とテスト用にデータを分割（分け方を毎回同じにしている）
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

#学習モデルを定義
model = models.Sequential([
    layers.Input(shape=(128, 128, 3)), #入力の形（128 x 128 ピクセル、3チャンネル（RGB）カラー画像）
    layers.Conv2D(32, (3, 3), activation='relu'), #画像から特徴を取り出すフィルター32個、3x3 のフィルターを使用、relu関数を使用
    layers.MaxPooling2D(2), #画像を縮めて、重要な部分だけを残す 
    layers.Conv2D(64, (3, 3), activation='relu'), #より深く画像の特徴を見る
    layers.MaxPooling2D(2),
    layers.Flatten(), #データを一列に並べ、計算しやすいようにする
    layers.Dense(128, activation='relu'), # 128個のノードで学習
    layers.Dense(5)  # 出力は5つ（カロリー、たんぱく質、脂質、炭水化物、塩分）
])
#学習方法を設定
#学習の進め方にadamを指定
#どれだけ答えとズレたかを計算する方法として、mse（平均二乗誤差）を指定
#どれくらいズレたかの平均を出す方法としてmae（平均絶対誤差）を指定
model.compile(optimizer='adam', loss='mse', metrics=['mae'])

#学習を実行
#1度に4枚ずつ80回くり返して学習する。全体のデータの10%をテスト用に残しておく
model.fit(X_train, y_train, epochs=80, batch_size=4, validation_split=0.1)

# === 保存 ===
model.save(MODEL_FILE) #学習モデルをMODEL_FILEに保存
print(f"モデルを保存しました: {MODEL_FILE}")

#テストデータで評価（精度の確認用）
loss, mae = model.evaluate(X_test, y_test)
print(f"テストデータに対する損失（loss）: {loss:.2f}")
print(f"平均絶対誤差（MAE）: {mae:.2f}")