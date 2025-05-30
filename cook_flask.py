#料理の栄養確認アプリ実行コード

#ライブラリのインポート
import os
from flask import Flask, request, render_template,redirect, send_from_directory,url_for, session
import numpy as np
from keras import models
from PIL import Image
import pandas as pd
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import pyotp

#---------------------------事前準備----------------------------

# ベースフォルダを取得
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
#アップロードした画像を保存するフォルダを指定
UPLOAD_FOLDER = os.path.join(BASE_DIR, "data", "uploads")
#学習モデルのフォルダを指定
MODEL_FILE = os.path.join(BASE_DIR, "data", "nutrition_model.keras")
#栄養素データCSVのフォルダを指定
CSV_FILE = os.path.join(BASE_DIR, "data", "nutrition.csv")
# 栄養素の項目を設定
LABELS = ["カロリー(kcal)", "たんぱく質(g)", "脂質(g)", "炭水化物(g)", "食塩相当量(g)"]
#画面の表示設定
CSS_URL = "https://cdn.jsdelivr.net/npm/bulma@1.0.2/css/bulma.min.css"
HTML_HEADER = f"""
<!DOCTYPE html><html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="{CSS_URL}">
<style>
/*スマホの画面（600px以下）のときに文字やボタンを大きくする*/
@media screen and (max-width: 600px) {{
    body {{
        font-size: 1em;
    }}
    input, button, .button {{
        font-size: 1em;
    }}
    h1, h2 {{
        font-size: 1em;
    }}
}}
</style>
</head>
<body>
<section class="hero has-background-info"><div class="hero-body">
    <h1 class="title">料理画像から栄養を予測</h1></div></section>
"""

#Flask アプリを作る準備
app = Flask(__name__)
#アップロードした画像を保存するフォルダを設定
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#予測した画像を格納するフォルダがなければ作成する。既に作成されていてもエラーは起きない。
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
#学習モデルを読み込む
model = models.load_model(MODEL_FILE)
#栄養素データCSVを読み込む
df = pd.read_csv(CSV_FILE)

#---------------------------ログイン機能----------------------------

#メールサーバーの設定 ---
app.secret_key = os.environ.get('SECRET_KEY')
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT']=587
app.config['MAIL_USE_TLS']=True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER')

#メール送信の機能を組み込む
mail = Mail(app)

#データベースの設定 ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db' #データベースの種類と場所を指定
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #データが変わったときに細かい追跡はしない

#アプリとデータベースを繋ぐ
db = SQLAlchemy(app)

#ID、メールアドレス、パスワードを管理設定する関数（User）を定義
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) #IDを作る（数字、一人一つ存在する）
    email = db.Column(db.String(150), unique=True, nullable=False) #メールアドレスを作る（150文字以内、重複不可、空欄禁止）
    password = db.Column(db.String(150), nullable=False) #パスワードを作る（150文字以内、空欄禁止）

#ユーザー認証の設定
login_manager = LoginManager() #ログイン機能を使えるようにする
login_manager.init_app(app) #アプリとログイン機能を連携させる

#ユーザーのIDを使ってデータを取得する関数
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#ワンタイムパスワードをメールで送信する関数
def send_otp(email, secret):
    #secretを使って、60秒ごとに変わるワンタイムパスワードをつくる
    totp = pyotp.TOTP(secret, interval=60)
    #現時点で使えるワンタイムパスワードの数字を作る
    otp_code = totp.now()

    #メールの内容をつくる
    msg = Message('ワンタイムパスワード（OTP）', recipients=[email])
    msg.body = f"あなたのワンタイムパスワードは {otp_code} です。60秒間有効です"

    #メールを送信
    mail.send(msg) 

#ユーザー登録ページの設定
@app.route('/register', methods=['GET', 'POST'])
#新しいユーザーを登録するための関数
def register():
    #もし登録ボタンを押したら
    if request.method == 'POST':
        #フォームに入力されたメールとパスワードを取り出す
        email = request.form['email']
        password = request.form['password']
        
        #ユーザーが既に存在するかを確認
        existing_user = User.query.filter_by(email=email).first() #データベースから、そのメールアドレスがすでに使われてないか確認
        #もし同じメールの人がすでに登録されていたら
        if existing_user:
            return '既に登録されているメールアドレスです。' #メッセージを表示
        
        # 新しいユーザーをデータベースに追加
        new_user = User(email=email, password=password) #新しいユーザーの情報を設定
        db.session.add(new_user) #新しいユーザーをデータベースに追加する準備
        db.session.commit() #新しいユーザーをデータベースに追加を確定
        
        #ログイン画面に遷移
        return redirect(url_for('login'))

    #登録フォームの画面を表示
    return render_template('register.html')

#トップページ（ログイン画面）の設定
@app.route('/', methods=['GET', 'POST'])
def login():
    #ログインボタンを押したら
    if request.method == 'POST':
        #フォームに入力されたメールとパスワードを取り出す
        email = request.form['email']
        password = request.form['password']

        #データベースからメールアドレスのユーザーを探す
        user = User.query.filter_by(email=email).first()

        #ユーザーが存在していて、パスワードも合っていたら
        if user and user.password == password:
            secret = pyotp.random_base32()  #ランダムなシークレットキーを生成
            #セッションにシークレットキーとメールアドレスを保存
            session['otp_secret'] = secret
            session['email'] = email
            #メール送信
            send_otp(email, secret) 

            #ワンタイムパスワード入力画面へ
            return redirect(url_for('verify')) 

        #メールやパスワードが違っていた場合
        return '認証情報が無効です。'

    #最初にページを開いたときなどは、ログイン画面を表示
    return render_template('login.html')


#ワンタイムパスワード検証するページの設定
@app.route('/verify', methods=['GET', 'POST'])
#ワンタイムパスワード検証する関数
def verify():
    #もし送信ボタンを押したら
    if request.method == 'POST':
        #フォームに入力されたワンタイムパスワードの数字を取り出す
        otp_code = request.form['otp']
        
        #ログインページでセッションに一時保存していたシークレットキーを取り出す
        secret = session.get('otp_secret')
        
        #シークレットキーを使って、ワンタイムパスワード生成器をもう一度作る
        totp = pyotp.TOTP(secret,interval=60)
        #入力されたワンタイムパスワードが、有効だったら
        if totp.verify(otp_code):
            #ログイン時に保存したメールアドレスを取り出す
            email = session.get('email')
            #そのメールアドレスのユーザーをデータベースから探す
            user = User.query.filter_by(email=email).first()
            #ユーザーが存在したら
            if user:
                #ログイン状態にする
                login_user(user)
                #ログイン成功したら、料理画像をアップロードできるページに遷移する
                return redirect(url_for('root'))
        #ワンタイムパスワードが間違っていたらメッセージを表示
        return '無効なOTPです。'

    #ワンタイムパスワードを入力する画面を表示
    return render_template('verify.html')

#---------------------------料理の栄養素判定機能----------------------------

#画像をアップロードして、栄養を予測するページの設定
@app.route("/select")
#ログインしているユーザーにしか見られないようにする
@login_required
def root():
    #HTML（Webページの見た目）を文字として設定
    #画像をアップロードするボタンや実行ボタンの配置。
    #実行ボタンを押したら予測画面に遷移
    return f"""{HTML_HEADER}
    <div class="box file">
        <form method="post" action="/predict" enctype="multipart/form-data">
            <input type="file" name="file" class="file-label" /><br>
            <input type="submit" value="栄養予測を実行" class="button is-primary" />
        </form></div></body></html>
    """

#AIモデルに画像を投入し、栄養素を予測するページ
@app.route("/predict", methods=["POST"])
#ログインしているユーザーにしか見られないようにする
@login_required
#画像をアップロードして処理する関数
def upload_file():
    #画像ファイルをアップロードしなかったら、元のページに戻します
    if 'file' not in request.files:
        return redirect(request.url)

    #アップロードされた画像をfile変数に格納
    file = request.files['file']
    #画像の名前が .jpg か .jpeg で終わってなかったら、エラー画面を出す
    if not (file and file.filename.endswith(('.jpg', '.jpeg'))):
        return f"""{HTML_HEADER}<h1>画像ファイルをアップロードしてください</h1></body></html>"""

    #画像名を設定
    filename = file.filename
    #アップロード画像の保存先を設定
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    #アップロード画像を保存
    file.save(file_path)

    #以下を実行する
    try:
        #画像を開き、128x128 サイズ・カラーに変換する
        img = Image.open(file_path).resize((128, 128)).convert("RGB")
        #画像を画像を0〜1の数字に変える。
        X = np.array([np.array(img) / 255.0])
    #エラーの場合、以下を実行する
    except Exception as e:
        #エラーメッセージを表示
        return f"""{HTML_HEADER}<h1>画像の読み込みに失敗しました</h1></body></html>"""

    # 予測を実行
    pred = model.predict([X])[0]

    # 実際の値を取得（同じ画像名がnutrition.csvにある場合）
    actual_row = df[df['filename'] == filename] #正解の栄養データがCSVにあるか探す。
    #もし正解データがあるなら
    if not actual_row.empty:
        #栄養素の値を取得
        actual = actual_row.iloc[0][["calorie", "protein", "fat", "carbo", "salt"]].values
        #予測との差を取得
        diff = np.abs(pred - actual)
        #HTMLの表を作って、「予測・正解・誤差」を表示
        result_table = "".join([
            f"<tr><td>{label}</td><td>{p:.1f}</td><td>{a:.1f}</td><td>{d:.1f}</td></tr>"
            for label, p, a, d in zip(LABELS, pred, actual, diff)
        ])
        table_header = "<thead><tr><th>項目</th><th>予測値</th><th>実際の値</th><th>誤差</th></tr></thead>"
    #正解データがないなら
    else:
        #予測結果だけを表に表示
        result_table = "".join([
            f"<tr><td>{label}</td><td>{value:.1f}</td></tr>"
            for label, value in zip(LABELS, pred)
        ])
        table_header = "<thead><tr><th>項目</th><th>予測値</th></tr></thead>"

    #「予測結果」、「料理写真」、「別の画像を試すボタン」を画面に表示
    return f"""{HTML_HEADER}
    <div class="card" style="font-size:1.2em; padding:1em;">
        <h2 class="title is-4">予測結果</h2>
        <table class="table is-striped">
            {table_header}
            <tbody>{result_table}</tbody>
        </table>
        <img src="/uploads/{filename}" width="300"><br>
        <a href="/select" class="button mt-4">別の画像を試す</a>
    </div></body></html>
    """

#アップロードされた画像をブラウザに表示するためのページを設定
@app.route("/uploads/<filename>")
##ログインしているユーザーにしか見られないようにする
@login_required
#画像をて表示する関数
def uploaded_file(filename):
    #UPLOAD_FOLDERにある画像を表示する
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


#---------------------------その他設定----------------------------

#データベースにユーザーテーブルを作るための設定
with app.app_context():
    #データベースの中にユーザーテーブルを作成
    db.create_all()

#アプリを動かすための設定
if __name__ == '__main__':
    #環境変数にポート番号があれば使用し、なければ10000を使用
    port = int(os.environ.get("PORT", 10000))
    #どこからのアクセス可能、上記ポート番号を指定、デバックなし
    app.run(host='0.0.0.0', port=port, debug=False)
