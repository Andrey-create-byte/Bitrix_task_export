import requests
import streamlit as st
import pandas as pd
import io
import json

# Получаем WEBHOOK_URL из secrets
WEBHOOK_URL = st.secrets["WEBHOOK_URL"]
TASK_ENDPOINT = WEBHOOK_URL + 'tasks.task.get'
COMMENTS_ENDPOINT = WEBHOOK_URL + 'task.commentitem.getlist'

# Функции
def fetch_task(task_id):
    params = {'taskId': task_id}
    response = requests.post(TASK_ENDPOINT, params=params).json()
    if 'result' in response and 'task' in response['result']:
        return response['result']['task']
    else:
        st.error(f"Не удалось получить задачу {task_id}. Ответ: {response}")
        return None

def fetch_comments(task_id):
    comments = []
    start = 0
    while True:
        params = {'TASK_ID': task_id, 'start': start}
        response = requests.post(COMMENTS_ENDPOINT, params=params).json()
        if 'result' not in response or 'commentItems' not in response['result']:
            st.error(f"Не удалось получить комментарии для задачи {task_id}. Ответ: {response}")
            break
        batch = response['result']['commentItems']
        comments.extend(batch)
        if 'next' in response['result']:
            start = response['result']['next']
        else:
            break
    return comments

def create_json_download(data, filename):
    json_data = json.dumps(data, ensure_ascii=False, indent=2)
    b = io.BytesIO()
    b.write(json_data.encode('utf-8'))
    b.seek(0)
    st.download_button(
        label=f"Скачать {filename}",
        data=b,
        file_name=filename,
        mime='application/json'
    )

# Streamlit-приложение
st.title("Экспорт одной задачи Bitrix24 в JSON")

task_id = st.text_input("Введите ID задачи:")

if st.button("Выгрузить задачу и комментарии"):
    if not task_id.strip():
        st.warning("Пожалуйста, введите ID задачи.")
    else:
        task_data = fetch_task(task_id)
        if task_data:
            st.subheader("Информация о задаче")
            st.json(task_data)
            create_json_download(task_data, f"task_{task_id}.json")

            comments = fetch_comments(task_id)
            if comments:
                st.subheader("Комментарии к задаче")
                st.json(comments)
                create_json_download(comments, f"comments_task_{task_id}.json")
            else:
                st.info("У задачи нет комментариев.")