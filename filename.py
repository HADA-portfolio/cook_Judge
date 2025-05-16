import os
import csv

# 対象フォルダのパスを指定（ご自身の環境に合わせて変更）
folder_path = 'C:/Users/tsuku/flask_workspace/cook_flask/data/augmented_images/images'


# 拡張子が画像のファイルを抽出
image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]

# CSVとして保存
csv_path = os.path.join(folder_path, 'image_filenames.csv')
with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['filename'])  # ヘッダー
    for name in image_files:
        writer.writerow([name])

print(f'画像ファイル名を {csv_path} に保存しました')
