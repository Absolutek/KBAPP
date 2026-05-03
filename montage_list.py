import flet as ft
import requests

TOKEN = "vhd0WTv1bqvn9dnYomoY9ye9aFLXcaiJLrdshigxKReJJha6"

# Переменные для списка записей
records_dropdown = None
selected_record_id = None
records = []
API_URL = None

def load_records():
    """Загружает список записей из API"""
    headers = {
        "X-Auth-Token": TOKEN
    }
    
    filter_url = "https://cb-test.jsdf.ru/api/dev/data160?filter=and(contains(f17460, '43'), not(contains(f10200, 'SENDED')))"
    
    try:
        response = requests.get(filter_url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            records_list = data.get('data', [])
            
            dropdown_options = []
            for record in records_list:
                attributes = record.get('attributes', {})
                record_id = record.get('id')
                field_f1980 = attributes.get('f1980', '')
                if field_f1980:
                    display_name = f"{record_id} - {field_f1980}"
                else:
                    display_name = f"{record_id} - (без названия)"
                dropdown_options.append(ft.dropdown.Option(record.get('id'), display_name))
            
            return records_list, dropdown_options
        else:
            print(f"Ошибка загрузки записей: {response.status_code}")
            return [], []
    except Exception as e:
        print(f"Ошибка соединения: {str(e)}")
        return [], []

def main(page: ft.Page):
    global API_URL, records_dropdown, selected_record_id, records, send_button, status_label
    
    page.title = "ClientBase - Обновление примечания"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    
    # Поле для ввода текста
    text_field = ft.TextField(
        label="Введите текст",
        hint_text="Сюда будет сохранено значение в f17560",
        width=400,
        multiline=True,
        min_lines=3,
        max_lines=5
    )
    
    # Статус сообщение
    status_label = ft.Text("", color=ft.Colors.GREY)
    
    # Загружаем записи
    records_list, dropdown_options = load_records()
    
    # Обработчик изменения выбранной записи (ВНУТРИ main)
    def on_record_change(e):
        global selected_record_id, API_URL, send_button, status_label
        
        selected_record_id = e.control.value
        if selected_record_id:
            API_URL = f"https://cb-test.jsdf.ru/api/dev/data160/{selected_record_id}"
            status_label.value = f"✅ Выбрана запись ID: {selected_record_id}"
            status_label.color = ft.Colors.GREEN
            send_button.disabled = False
        else:
            send_button.disabled = True
            status_label.value = "❌ Выберите запись"
            status_label.color = ft.Colors.RED
        
        page.update()  # page доступна из внешней функции
    
    # Создаем выпадающий список
    records_dropdown = ft.Dropdown(
        label="Выберите запись",
        hint_text="Выберите запись из списка",
        width=400,
        options=dropdown_options,
        on_select=on_record_change,
        disabled=len(dropdown_options) == 0
    )
    
    # Если список пуст, показываем сообщение
    if len(dropdown_options) == 0:
        status_label.value = "❌ Нет доступных записей для выбора"
        status_label.color = ft.Colors.RED
    
    def close_dialog(e):
        dialog.open = False
        page.update()
    
    def open_change_again(e):
        dialog.open = False
        text_field.value = ""
        text_field.focus()
        page.update()
    
    # Создаем диалоговое окно
    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("✅ Успешно!", size=24, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
        content=ft.Text("", text_align=ft.TextAlign.CENTER),
        actions=[
            ft.TextButton("Изменить снова", on_click=open_change_again, style=ft.ButtonStyle(color=ft.Colors.BLUE)),
            ft.TextButton("Закрыть", on_click=close_dialog, style=ft.ButtonStyle(color=ft.Colors.GREY)),
        ],
        actions_alignment=ft.MainAxisAlignment.CENTER,
    )
    
    # Кнопка отправки
    def send_text(e):
        if not selected_record_id:
            status_label.value = "❌ Сначала выберите запись из списка"
            status_label.color = ft.Colors.RED
            page.update()
            return
        
        if not API_URL:
            status_label.value = "❌ URL не установлен. Выберите запись."
            status_label.color = ft.Colors.RED
            page.update()
            return
        
        user_text = text_field.value.strip()
        
        if not user_text:
            status_label.value = "❌ Введите текст перед отправкой"
            status_label.color = ft.Colors.RED
            page.update()
            return
        
        headers = {
            "Content-Type": "application/vnd.api+json",
            "X-Auth-Token": TOKEN
        }
        
        payload = {
            "data": {
                "type": "data160",
                "id": selected_record_id,
                "attributes": {
                    "f17560": user_text
                }
            }
        }
        
        status_label.value = "⏳ Отправка..."
        status_label.color = ft.Colors.BLUE
        page.update()
        
        try:
            response = requests.patch(API_URL, headers=headers, json=payload)
            
            if response.status_code == 200:
                dialog.content = ft.Text(
                    f"Значение '{user_text}' успешно сохранено в поле примечание заявки № {selected_record_id}",
                    size=16,
                    text_align=ft.TextAlign.CENTER
                )
                page.overlay.append(dialog)
                dialog.open = True
                text_field.value = ""
                status_label.value = ""
                page.update()
            else:
                status_label.value = f"❌ Ошибка {response.status_code}: {response.text[:200]}"
                status_label.color = ft.Colors.RED
                page.update()
        except Exception as e:
            status_label.value = f"❌ Ошибка соединения: {str(e)}"
            status_label.color = ft.Colors.RED
            page.update()
    
    send_button = ft.ElevatedButton(
        "Отправить",
        on_click=send_text,
        width=200,
        disabled=True,
        style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.BLUE)
    )
    
    page.add(
        ft.Column(
            [
                ft.Text("Изменение поля f17560", size=24, weight=ft.FontWeight.BOLD),
                ft.Divider(height=20),
                records_dropdown,
                ft.Container(height=10),
                text_field,
                ft.Container(height=10),
                send_button,
                ft.Container(height=20),
                status_label
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10
        )
    )

if __name__ == "__main__":
    ft.app(target=main)