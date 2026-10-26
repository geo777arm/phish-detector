# Проверка твоего кода (это делает Claude).
# Запуск:  python3 check.py
# Цель: все строчки с ✅.

import csv
import os
import pickle

import rules

PHISH_MIN = 50   # фишинговое письмо должно набрать хотя бы столько баллов
SAFE_MAX = 30    # обычное письмо должно набрать не больше

with open("data/sample_emails.csv", encoding="utf-8") as f:
    emails = list(csv.DictReader(f))

passed = total = 0


def report(ok, text):
    global passed, total
    total += 1
    passed += ok
    print(("✅ " if ok else "❌ ") + text)


print("\n── Правила (rules.py) ──")
for e in emails:
    signs = rules.check_email(e["text"])
    score = min(100, sum(p for _, p in signs))
    short = e["text"][:60] + "…"
    if e["label"] == "1":
        report(score >= PHISH_MIN, f"фишинг, {score} баллов (нужно ≥ {PHISH_MIN}): {short}")
    else:
        report(score <= SAFE_MAX, f"обычное, {score} баллов (нужно ≤ {SAFE_MAX}): {short}")

print("\n── Модель (train_model.py) ──")
if not os.path.exists("model.pkl"):
    report(False, "файла model.pkl пока нет: запусти python3 train_model.py")
else:
    with open("model.pkl", "rb") as f:
        model = pickle.load(f)
    report(hasattr(model, "predict_proba"), "модель умеет считать вероятность (predict_proba)")
    texts = [e["text"] for e in emails]
    labels = [int(e["label"]) for e in emails]
    accuracy = sum(int(p) == l for p, l in zip(model.predict(texts), labels)) / len(labels)
    report(accuracy >= 0.8, f"точность на тестовых письмах {accuracy:.0%} (нужно ≥ 80%)")

print(f"\nПройдено: {passed} из {total}\n")
