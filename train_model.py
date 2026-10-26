import pickle

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline

DATA_PATH = "data/phishing_email.csv"
RUSSIAN_PATH = "data/russian_emails.csv"

# 1. Читаем таблицу с письмами (английская база с Kaggle)
table = pd.read_csv(DATA_PATH)

# 2. Тексты писем и правильные ответы (1 = фишинг, 0 = обычное)
X = table["text_combined"]
y = table["label"]

# 3. Делим: 80% писем учат модель, 20% проверяют
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 3.5. Добавляем русские письма в обучение.
# Их всего 90 против 66 000 английских, поэтому повторяем их 20 раз,
# иначе модель их почти не заметит.
russian = pd.read_csv(RUSSIAN_PATH)
X_train = pd.concat([X_train] + [russian["text"]] * 20)
y_train = pd.concat([y_train] + [russian["label"]] * 20)

# 4. Собираем модель: текст → числа → решение
model = make_pipeline(TfidfVectorizer(), LogisticRegression(max_iter=1000))

# 5. Учим модель на учебных письмах
model.fit(X_train, y_train)

# 6. Проверяем на письмах, которых она не видела
accuracy = model.score(X_test, y_test)
print("Точность:", round(accuracy * 100), "%")

# 7. Сохраняем модель в файл
with open("model.pkl", "wb") as f:
    pickle.dump(model, f)

print("Модель сохранена в model.pkl")
