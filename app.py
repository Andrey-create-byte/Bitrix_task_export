import requests
import json
import streamlit as st

# Чтение секрета из Streamlit secrets
WEBHOOK_URL = st.secrets["WEBHOOK_URL"]

# Функции для запросов к Bitrix24 API
def get_task(task_id):
    url = f"{WEBHOOK_URL}tasks.task.get"
    params = {"taskId": task_id}
    response = requests.get(url, params=params)
    return response.json()

def get_task_comments(task_id):
    url = f"{WEBHOOK_URL}task.commentitem.getlist"
    params = {"TASKID": task_id}
    response = requests.get(url, params=params)
    return response.json()

def get_task_history(task_id):
    url = f"{WEBHOOK_URL}task.history.list"
    params = {"TASK_ID": task_id}
    response = requests.get(url, params=params)
    return response.json()

# Основной процесс
if __name__ == "__main__":
    st.title("Экспорт задачи Bitrix24: задача, RAW комментарии и история изменений")

    task_id = st.number_input("Введите ID задачи", value=11559)
    if st.button("Выгрузить данные"):

        # 1. Загружаем все данные
        task_data = get_task(task_id)
        comments_data_raw = get_task_comments(task_id)
        history_data_raw = get_task_history(task_id)

        # 2. Сохраняем JSON задачи
        filename_json_task = f"task_{task_id}.json"
        with open(filename_json_task, "w", encoding="utf-8") as f:
            json.dump(task_data, f, indent=2, ensure_ascii=False)

        with open(filename_json_task, "r", encoding="utf-8") as f:
            st.download_button('Скачать JSON задачи', f, file_name=filename_json_task, mime='application/json')

        # 3. Сохраняем RAW комментарии в JSON
        filename_json_comments = f"task_{task_id}_raw_comments.json"
        with open(filename_json_comments, "w", encoding="utf-8") as f:
            json.dump(comments_data_raw, f, indent=2, ensure_ascii=False)

        with open(filename_json_comments, "r", encoding="utf-8") as f:
            st.download_button('Скачать RAW JSON комментариев', f, file_name=filename_json_comments, mime='application/json')

        # 4. Сохраняем историю изменений в TXT
        filename_txt_history = f"task_{task_id}_history.txt"
        with open(filename_txt_history, "w", encoding="utf-8") as f:
            json.dump(history_data_raw, f, indent=2, ensure_ascii=False)

        with open(filename_txt_history, "r", encoding="utf-8") as f:
            st.download_button('Скачать RAW JSON истории изменений', f, file_name=filename_txt_history, mime='application/json')
