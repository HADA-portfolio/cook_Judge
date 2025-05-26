#画像ファイル名を抽出し、CSVファイルに一覧として保存するコード

#ライブラリのインポート
import os
import csv

# 画像フォルダのパスを指定
folder_path = 'C:/Users/tsuku/flask_workspace/cook_flask/data/augmented_images/images'

# 画像名を抽出（拡張子は「jpg」,「.jpeg」,「.png」に限定）
image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]

# CSVとして保存
csv_path = os.path.join(folder_path, 'image_filenames.csv') #保存先と保存名を指定
with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:#CSVファイルを書き込み用に開いて、csvfileという名前で使えるようにする
    writer = csv.writer(csvfile) #CSVに文字を書きこむ準備
    writer.writerow(['filename'])  #CSVの1行目に「filename」を書く
    for name in image_files: #画像名を取り出す
        writer.writerow([name]) #画像名を書き出す

#保存した旨メッセージを表示
print(f'画像ファイル名を {csv_path} に保存しました')
