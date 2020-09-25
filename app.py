import os
# flaskのインポート
from flask import *
# ファイル名をチェックする関数
from werkzeug.utils import secure_filename
# 画像のダウンロード
from flask import send_from_directory
# 画像処理用
import cv2
# CORS有効化用
from flask_cors import CORS
# 時間取得用
import time


# 画像のアップロード先のディレクトリ
UPLOAD_FOLDER = 'src/upload/'
RESULT_FOLDER = 'src/face/'

# アップロードされる拡張子の制限
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'gif'])

# Flaskの宣言
app = Flask(__name__)
CORS(app)                   # CORS有効化
app.secret_key = 'hogehoge' # アクセスキーのやつ（これがないとエラーに）

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULT_FOLDER'] = RESULT_FOLDER


# 拡張子の確認
def allwed_file(filename):
    # .があるかどうかのチェックと、拡張子の確認
    # OKなら１、だめなら0
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# 顔認識
def face_recognition(target_img):
    target_img = UPLOAD_FOLDER + target_img
    # 入力画像を読み込み
    img = cv2.imread(target_img)

    # カスケード型識別器の読み込み
    cascade = cv2.CascadeClassifier("./lib/opencv/data/haarcascades/haarcascade_frontalface_default.xml")

    # グレースケール変換
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 顔領域の探索
    face = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=3, minSize=(30, 30))

    # 顔領域を赤色の矩形で囲む
    for (x, y, w, h) in face:
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 200), 3)

    # 結果の出力
    output_file = RESULT_FOLDER + str(time.time()) + ".png"
    cv2.imwrite(output_file, img)
    return output_file, len(face)


# ファイルを受け取る方法の指定
@app.route('/face', methods=['GET', 'POST'])
def uploads_file():
    # リクエストがポストかどうかの判別
    if request.method == 'POST':
        print(request.files)

        # ファイルがなかった場合の処理
        if 'file' not in request.files:
            return 'file not found in request'

        # データの取り出し
        file = request.files['file']
        # ファイル名が空の時の処理
        if file.filename == '':
            return 'file name is null'

        # ファイルのチェック
        if file and allwed_file(file.filename):
            # 危険な文字を削除（サニタイズ処理）
            filename = secure_filename(file.filename)
            # ファイルの保存
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # 画像を変換
            convert_img, people = face_recognition(filename)

            # JSONを返す
            return jsonify('{ \"img\": \"' + str(convert_img) + '\", \"people\": \"' + str(people) + '\"}')
    return 'error'


# ファイルを表示する
@app.route('/' + RESULT_FOLDER + '<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['RESULT_FOLDER'], filename)


if __name__ == '__main__':
    app.run()
