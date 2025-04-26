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
    st.title("Экспорт задачи Bitrix24 с комментариями и историей")

    task_id = st.number_input("Введите ID задачи", value=11559)
    if st.button("Выгрузить задачу, комментарии и историю"):

        # Запросы данных
        task_data = get_task(task_id)
        comments_data_raw = get_task_comments(task_id)
        history_data_raw = get_task_history(task_id)

        # Извлечение данных о задаче
        task = task_data.get("result", {}).get("task", {})

        # Корректная обработка комментариев
        comments = []
        if comments_data_raw and isinstance(comments_data_raw, dict):
            result = comments_data_raw.get("result")
            if isinstance(result, list):
                comments = result

        # Корректная обработка истории изменений
        history = []
        if history_data_raw and isinstance(history_data_raw, dict):
            result = history_data_raw.get("result")
            if isinstance(result, list):
                history = result

        # Сохраняем JSON задачи
        filename_json = f"task_{task_id}.json"
        with open(filename_json, "w", encoding="utf-8") as f:
            json.dump(task, f, indent=2, ensure_ascii=False)

        st.success(f"Задача {task_id} успешно выгружена.")
        with open(filename_json, "r", encoding="utf-8") as f:
            st.download_button('Скачать JSON задачи', f, file_name=filename_json, mime='application/json')

        # Сохраняем комментарии в TXT
        filename_txt_comments = f"task_{task_id}_comments.txt"
        with open(filename_txt_comments, "w", encoding="utf-8") as f:
            if not comments:
                f.write("Комментариев нет.\n")
            else:
                f.write(f"Всего комментариев: {len(comments)}\n\n")
                for idx, comment in enumerate(comments, start=1):
                    author = comment.get("AUTHOR_NAME", "Неизвестный автор")
                    date = comment.get("POST_DATE", "Нет даты")

                    # Корректная обработка POST_MESSAGE
                    message = ""
                    if isinstance(comment.get("POST_MESSAGE"), dict):
                        message = comment.get("POST_MESSAGE", {}).get("VALUE", "")
                    else:
                        message = comment.get("POST_MESSAGE", "")

                    if not message:
                        if isinstance(comment.get("POST_MESSAGE_HTML"), dict):
                            message = comment.get("POST_MESSAGE_HTML", {}).get("VALUE", "")
                        else:
                            message = comment.get("POST_MESSAGE_HTML", "")

                    if not message:
                        message = "Комментарий отсутствует"

                    f.write(f"Комментарий №{idx}\n")
                    f.write(f"Автор: {author}\n")
                    f.write(f"Дата: {date}\n")
                    f.write(f"Сообщение:\n{message}\n")
                    f.write("-" * 50 + "\n\n")

        with open(filename_txt_comments, "r", encoding="utf-8") as f:
            st.download_button('Скачать TXT комментариев', f, file_name=filename_txt_comments, mime='text/plain')

        # Сохраняем историю изменений в TXT
        filename_txt_history = f"task_{task_id}_history.txt"
        with open(filename_txt_history, "w", encoding="utf-8") as f:
            if not history:
                f.write("История изменений отсутствует.\n")
            else:
                f.write(f"Всего событий в истории: {len(history)}\n\n")
                for idx, event in enumerate(history, start=1):
                    field = event.get("FIELD", "Не указано")
                    from_value = event.get("FROM_VALUE", "")
                    to_value = event.get("TO_VALUE", "")
                    created_date = event.get("CREATED_DATE", "")
                    user_id = event.get("USER_ID", "")

                    f.write(f"Изменение №{idx}\n")
                    f.write(f"Дата изменения: {created_date}\n")
                    f.write(f"Поле: {field}\n")
                    f.write(f"Старое значение: {from_value}\n")
                    f.write(f"Новое значение: {to_value}\n")
                    f.write(f"Изменил пользователь (ID): {user_id}\n")
                    f.write("-" * 50 + "\n\n")

        with open(filename_txt_history, "r", encoding="utf-8") as f:
            st.download_button('Скачать TXT истории изменений', f, file_name=filename_txt_history, mime='text/plain')
