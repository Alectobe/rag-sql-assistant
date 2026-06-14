"""Minimal Streamlit UI. Calls the pipeline directly for dev simplicity.

Run from the project root:  streamlit run ui/streamlit_app.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st  # noqa: E402

from app.config import settings  # noqa: E402
from app.pipeline import ask  # noqa: E402

st.set_page_config(page_title="RAG SQL Assistant", layout="wide")
st.title("RAG SQL-ассистент для аналитики")
st.caption(f"Бэкенд: {settings.llm_backend} · модель: {settings.generation_model}")

question = st.text_input("Вопрос к данным", placeholder="Сколько активных пользователей было вчера?")

if st.button("Спросить", type="primary") and question.strip():
    with st.spinner("Генерирую SQL и выполняю..."):
        result = ask(question.strip())

    if result.error:
        st.error(f"Не удалось получить ответ: {result.error}")
    else:
        st.subheader("Ответ")
        st.write(result.answer)
        if result.notes:
            st.caption(f"Трактовка: {result.notes}")

    if result.sql:
        st.subheader("SQL")
        st.code(result.sql, language="sql")

    if result.rows:
        st.subheader("Результат")
        st.dataframe({col: [row[i] for row in result.rows]
                      for i, col in enumerate(result.columns)})

    st.caption(f"Попыток: {result.attempts}")
