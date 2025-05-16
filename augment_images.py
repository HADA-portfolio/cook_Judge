#画像を反転・角度調整するためのコード

import os
from PIL import Image, ImageEnhance
import numpy as np

# ベースディレクトリを取得（Azureでもローカルでも動く）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# アップロードフォルダとモデルファイルのパスを設定
INPUT_FOLDER = os.path.join(BASE_DIR, "data", "images")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "data", "augmented_images", "images")
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# 拡張関数
def augment_image(img, basename):
    count = 0

    # 1. オリジナル
    img.save(f"{OUTPUT_FOLDER}/{basename}_orig.jpg")
    count += 1

    # 2. 左右反転
    flipped = img.transpose(Image.FLIP_LEFT_RIGHT)
    flipped.save(f"{OUTPUT_FOLDER}/{basename}_flip.jpg")
    count += 1

    # 3. 回転 -15, +15 度
    for angle in [-15, 15]:
        rotated = img.rotate(angle, expand=True)
        rotated.save(f"{OUTPUT_FOLDER}/{basename}_rot{angle}.jpg")
        count += 1

    # 4. 明るさ変更（80%, 120%）
    for factor in [0.8, 1.2]:
        enhancer = ImageEnhance.Brightness(img)
        bright = enhancer.enhance(factor)
        bright.save(f"{OUTPUT_FOLDER}/{basename}_bright{int(factor*100)}.jpg")
        count += 1

    return count

# 実行
total = 0
for filename in os.listdir(INPUT_FOLDER):
    if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
        path = os.path.join(INPUT_FOLDER, filename)
        img = Image.open(path).convert('RGB')
        basename = os.path.splitext(filename)[0]
        total += augment_image(img, basename)

print(f"拡張画像を合計 {total} 枚保存しました。")
