# Оболочка детектора (это делает Claude).
# Запуск:  python app.py   →   открой http://127.0.0.1:5050
#
# Твой код живёт в rules.py и train_model.py, этот файл его только вызывает.

import os
import pickle

from flask import Flask, jsonify, render_template, request

import rules

app = Flask(__name__)
MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")


def load_model():
    """Модель появится, когда ты запустишь train_model.py."""
    if not os.path.exists(MODEL_PATH):
        return None
    with open(MODEL_PATH, "rb") as f:
        return pickle.load(f)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    text = (request.get_json() or {}).get("text", "")

    signs = rules.check_email(text)
    rules_score = min(100, sum(points for _, points in signs))

    model = load_model()
    model_score = None
    if model is not None:
        model_score = round(model.predict_proba([text])[0][1] * 100)

    # Если модель есть, итог — среднее правил и модели. Если нет, только правила.
    score = rules_score if model_score is None else round((rules_score + model_score) / 2)

    return jsonify({
        "score": score,
        "rules_score": rules_score,
        "model_score": model_score,
        "signs": [{"reason": reason, "points": points} for reason, points in signs],
    })


if __name__ == "__main__":
    app.run(debug=True, port=5050)
