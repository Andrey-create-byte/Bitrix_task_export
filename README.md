# Экспорт одной задачи Bitrix24 в JSON через Streamlit

Простое приложение на Streamlit для экспорта одной задачи и её комментариев в формате JSON.

## Установка

1. Клонируйте репозиторий или скачайте проект.
2. Установите зависимости:
```bash
pip install -r requirements.txt
```
3. Запустите приложение:
```bash
streamlit run app.py
```

## Настройки

- Перед использованием создайте файл `.streamlit/secrets.toml` и добавьте в него ваш WEBHOOK_URL.

Пример файла `.streamlit/secrets.toml`:

```toml
[general]
WEBHOOK_URL = "https://yourcompany.bitrix24.ru/rest/1/abc123xyz/"
```

Или настройте секреты через Streamlit Cloud при деплое.