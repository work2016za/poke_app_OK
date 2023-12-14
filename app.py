from flask import Flask, render_template, request, make_response, jsonify
from googletrans import Translator
import pyttsx3
import requests
import random

app = Flask(__name__)

engine = pyttsx3.init()

# ポケモンAPIのベースURL
base_url = 'https://pokeapi.co/api/v2/pokemon/'

# ランダムなポケモンの取得
def get_random_pokemon():
    # ポケモンのIDをランダムに選択
    pokemon_id = random.randint(1, 151)  # 1から151までのポケモンが存在します

    # ポケモンAPIからデータを取得
    response = requests.get(f'{base_url}{pokemon_id}')
    if response.status_code == 200:
        pokemon_data = response.json()
        return pokemon_data
    else:
        return None

# 翻訳履歴を格納するリスト
translation_history = []

# ルートパスへのリクエストを処理する
@app.route("/")
def index():
    # ランダムなポケモンのデータを取得
    pokemon_data = get_random_pokemon()

    # 履歴をクッキーから取得
    translation_history = request.cookies.get('translation_history')
    if translation_history:
        translation_history = eval(translation_history)
    else:
        translation_history = []

    # 履歴と共にテンプレートにデータを渡してレンダリング
    return render_template('index.html', pokemon_data=pokemon_data, translation_history=translation_history)

# /translate ルートを追加し、翻訳を実行
@app.route("/translate", methods=["POST"])
def translate():
    if request.method == "POST":
        text = request.form["text"]
        target_lang = request.form["target_lang"]
        translated_text = call_google_translate(text, target_lang)
        
        # 翻訳履歴をクッキーから取得
        translation_history = request.cookies.get('translation_history')
        if translation_history:
            translation_history = eval(translation_history)
        else:
            translation_history = []

        # 新しい翻訳を履歴に追加
        translation_history.append((text, translated_text))

        # クッキーに翻訳履歴を保存
        response = make_response(render_template('index.html', text=text, translated_text=translated_text, pokemon_data=get_random_pokemon(), translation_history=translation_history))
        response.set_cookie('translation_history', str(translation_history))

        # Google Translateで翻訳したテキストを読み上げる
        read_text_aloud(translated_text)

        return response

def call_google_translate(text, target_lang):
    translator = Translator()
    translated_text = translator.translate(text, dest=target_lang)
    return translated_text.text

def read_text_aloud(text):
    engine = pyttsx3.init()
    engine = pyttsx3.init("sapi5")
    engine.runAndWait()  

if __name__ == "__main__":
    app.debug = False
    app.run(debug=False, host='192.168.1.108', port=50001)
