import requests
import json
import csv
import streamlit as st

# Чтение секрета из Streamlit secrets
WEBHOOK_URL = st.secrets["WEBHOOK_URL"]

# Функции для запросов к Bitrix24 API
def get_task(task_id):
    url = f"{WEBHOOK_URL}tasks.task.get"
    params = {"taskId": task_id}
    response = requests.get(url, params=params)
    return response.json()

def get_task_history(task_id):
    url = f"{WEBHOOK_URL}task.history.list"
    params = {"TASK_ID": task_id}
    response = requests.get(url, params=params)
    return response.json()

def get_task_comments(task_id):
    url = f"{WEBHOOK_URL}task.commentitem.getlist"
    params = {"TASKID": task_id}
    response = requests.get(url, params=params)
    return response.json()

# Основной процесс
if __name__ == "__main__":
    st.title("Экспорт задачи Bitrix24 в JSON и комментариев в CSV")

    task_id = st.number_input("Введите ID задачи", value=11559)
    if st.button("Выгрузить задачу и комментарии"):
        # Запрос задачи, истории и комментариев
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

        # Сохраняем JSON с задачей
        filename_json = f"task_{task_id}.json"
        with open(filename_json, "w", encoding="utf-8") as f:
            json.dump(task, f, indent=2, ensure_ascii=False)

        st.success(f"Задача {task_id} успешно выгружена.")
        with open(filename_json, "r", encoding="utf-8") as f:
            st.download_button('Скачать JSON задачи', f, file_name=filename_json, mime='application/json')

        # Теперь обработка комментариев и сохранение в CSV
        comments = comments_data.get("result", [])
        filename_csv = f"task_{task_id}_comments.csv"
        with open(filename_csv, mode="w", newline="", encoding="utf-8") as csvfile:
            fieldnames = ["№", "Автор", "Дата", "Текст комментария"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for idx, comment in enumerate(comments, start=1):
                message = comment.get("POST_MESSAGE") or comment.get("POST_MESSAGE_HTML") or "Комментарий отсутствует"
                writer.writerow({
                    "№": idx,
                    "Автор": comment.get("AUTHOR_NAME", "Неизвестный автор"),
                    "Дата": comment.get("POST_DATE", "Нет даты"),
                    "Текст комментария": message
                })

        with open(filename_csv, "r", encoding="utf-8") as f:
            st.download_button('Скачать CSV комментариев', f, file_name=filename_csv, mime='text/csv')
