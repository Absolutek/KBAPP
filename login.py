import flet as ft
import requests

API_URL = "https://cb-test.jsdf.ru/api"

def main(page: ft.Page):
    page.title = "Клиент ClientBase"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # --- Экран входа (логин и пароль) ---
    login_input = ft.TextField(label="Логин", width=300)
    password_input = ft.TextField(label="Пароль", password=True, width=300)
    status_text = ft.Text("")
    data_table = ft.DataTable(columns=[ft.DataColumn(ft.Text("ID"))]) # Таблица для данных

    def login_click(e):
        # 1. Отправляем запрос на API
        response = requests.post(f"{API_URL}/auth", json={
            "login": login_input.value,
            "password": password_input.value
        })
        
        # 2. Обрабатываем ответ
        if response.status_code == 200:
            token = response.json().get('token')
            status_text.value = "Вход выполнен, загружаем данные..."
            page.update()
            
            # 3. Загружаем данные из таблицы 160 (как вы и хотели)
            headers = {"X-Auth-Token": token, "Content-Type": "application/vnd.api+json"}
            data_resp = requests.get(f"{API_URL}/dev/data160", headers=headers, params={"limit": 50})
            
            if data_resp.status_code == 200:
                data = data_resp.json().get('data', [])
                # Очищаем старые строки и добавляем новые
                data_table.rows.clear()
                for item in data:
                    data_table.rows.append(ft.DataRow(cells=[ft.DataCell(ft.Text(str(item.get('id'))))]))
                status_text.value = f"Готово! Загружено {len(data)} записей."
            else:
                status_text.value = f"Ошибка API: {data_resp.status_code}"
        else:
            status_text.value = "Ошибка входа"
        page.update()

    # --- Собираем всё на экран ---
    page.add(
        ft.Column([
            ft.Text("Демо-клиент ClientBase", size=20, weight="bold"),
            login_input,
            password_input,
            ft.ElevatedButton("Войти", on_click=login_click),
            status_text,
            ft.Container(content=data_table, padding=10) # Обертка для таблицы
        ], alignment=ft.MainAxisAlignment.CENTER)
    )

# Запуск
ft.app(target=main)