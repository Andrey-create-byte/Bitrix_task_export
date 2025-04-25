import requests import json import streamlit as st

Чтение секрета из Streamlit secrets

WEBHOOK_URL = st.secrets["WEBHOOK_URL"]

Функции для запросов к Bitrix24 API

def get_task(task_id): url = f"{WEBHOOK_URL}tasks.task.get" params = {"taskId": task_id} response = requests.get(url, params=params) return response.json()

def get_task_history(task_id): url = f"{WEBHOOK_URL}task.history.list" params = {"TASK_ID": task_id} response = requests.get(url, params=params) return response.json()

def get_task_comments(task_id): url = f"{WEBHOOK_URL}task.commentitem.getlist" params = {"TASKID": task_id} response = requests.get(url, params=params) return response.json()

Основной процесс

if name == "main": st.title("Экспорт задачи Bitrix24 в JSON")

task_id = st.number_input("Введите ID задачи", value=11559)
if st.button("Выгрузить задачу"):
    task_data = get_task(task_id)
    history_data = get_task_history(task_id)
    comments_data = get_task_comments(task_id)

    # Извлечь основные данные задачи
    task = task_data.get("result", {}).get("task", {})

    # Извлечь переносы сроков
    deadline_changes = []
    for event in history_data.get("result", []):
        if event.get("FIELD") == "DEADLINE":
            change = {
                "changed_by": event.get("USER_ID"),
                "changed_date": event.get("CREATED_DATE"),
                "old_deadline": event.get("FROM_VALUE"),
                "new_deadline": event.get("TO_VALUE")
            }
            deadline_changes.append(change)

    task["deadline_changes"] = deadline_changes

    # Извлечь комментарии
    comments = []
    for comment in comments_data.get("result", []):
        message = comment.get("POST_MESSAGE", "")
        if not message and "POST_MESSAGE_HTML" in comment:
            message = comment.get("POST_MESSAGE_HTML", "")

        comments.append({
            "author_id": comment.get("AUTHOR_ID"),
            "author_name": comment.get("AUTHOR_NAME"),
            "post_date": comment.get("POST_DATE"),
            "message": message
        })

    task["comments"] = comments

    # Сохраняем в JSON
    filename = f"task_{task_id}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(task, f, indent=2, ensure_ascii=False)

    st.success(f"Задача {task_id} успешно выгружена с историей переносов дедлайна и комментариями.")
    with open(filename, "r", encoding="utf-8") as f:
        st.download_button('Скачать JSON', f, file_name=filename, mime='application/json')

