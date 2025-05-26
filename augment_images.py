#画像を拡張（反転・角度・明るさ）するためのコード

#ライブラリのインポート
import os
from PIL import Image, ImageEnhance
import numpy as np

# ベースフォルダを取得
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

#元画像のフォルダパスと拡張画像のフォルダパスを設定
INPUT_FOLDER = os.path.join(BASE_DIR, "data", "images")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "data", "augmented_images", "images")

#拡張画像のフォルダパスがなければ作成する。既に作成されていてもエラーは起きない。
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# 画像を拡張する関数
def augment_image(img, basename):
    
    #画像の枚数を数えるためのカウント
    count = 0

    #オリジナル
    img.save(f"{OUTPUT_FOLDER}/{basename}_orig.jpg") #OUTPUT_FOLDERに、{basename}_orig.jpgの名前で画像を保存する
    #カウントを1追加する
    count += 1

    #左右反転
    flipped = img.transpose(Image.FLIP_LEFT_RIGHT)
    flipped.save(f"{OUTPUT_FOLDER}/{basename}_flip.jpg")
    count += 1

    #回転 -15, +15 度
    for angle in [-15, 15]:
        rotated = img.rotate(angle, expand=True) #画像の枠を自動で広げて、はみ出した部分も切り取らずに表示する
        rotated.save(f"{OUTPUT_FOLDER}/{basename}_rot{angle}.jpg")
        count += 1

    #明るさ変更（80%, 120%）
    for factor in [0.8, 1.2]:
        enhancer = ImageEnhance.Brightness(img) #画像の明るさを変える装置をセット
        bright = enhancer.enhance(factor) #実際に明るさを変えた画像を作り、bright変数に格納
        bright.save(f"{OUTPUT_FOLDER}/{basename}_bright{int(factor*100)}.jpg")
        count += 1

    #生成した画像の枚数を返す
    return count

#画像拡張を実行
total = 0 #画像の枚数カウントを最初を0にする
for filename in os.listdir(INPUT_FOLDER): #INPUT_FOLDERフォルダの中にある全てのファイルを取り出し、filename変数に入れる
    if filename.lower().endswith(('.jpg', '.jpeg', '.png')): #ファイル名の最後が「.jpg」「.jpeg」「.png」で終わってたら、
        path = os.path.join(INPUT_FOLDER, filename) #元画像のフォルダ名とファイル名をつなぎ、パスを作成する
        img = Image.open(path).convert('RGB') #画像を開き、カラーにする
        basename = os.path.splitext(filename)[0] #ファイル名から拡張子を切り取る
        total += augment_image(img, basename) #augment_image関数を実行する

#拡張画像の枚数カウントを表示する
print(f"拡張画像を合計 {total} 枚保存しました。")