import flet as ft
import requests
import base64
import os

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
    
    page.title = "ClientBase - Обновление примечания и фото"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    
    # Список для хранения выбранных файлов
    selected_files = []
    files_list_view = ft.Column(spacing=5)
    
    # Функция для обработки выбранных файлов (без явного типа)
    def pick_files_result(e):
        if e.files:
            for file in e.files:
                selected_files.append(file.path)
                files_list_view.controls.append(
                    ft.Row([
                        ft.Icon(ft.icons.IMAGE, size=20, color=ft.Colors.GREEN),
                        ft.Text(file.name, size=12, color=ft.Colors.BLACK),
                        ft.IconButton(
                            icon=ft.icons.CLOSE,
                            icon_size=16,
                            tooltip="Удалить",
                            on_click=lambda event, path=file.path: remove_file(path)
                        )
                    ])
                )
            page.update()
    
    def remove_file(file_path):
        for i, f in enumerate(selected_files):
            if f == file_path:
                selected_files.pop(i)
                files_list_view.controls.pop(i)
                break
        page.update()
    
    # Файл пикер для выбора изображений
    file_picker = ft.FilePicker(on_result=pick_files_result)
    page.overlay.append(file_picker)
    
    def take_photo(e):
        file_picker.pick_files(
            allowed_extensions=["jpg", "jpeg", "png", "gif", "bmp"],
            allow_multiple=True
        )
    
    # Поле "Фото проекта"
    photos_section = ft.Column([
        ft.Text("Фото проекта", size=16, weight=ft.FontWeight.BOLD),
        ft.Row([
            ft.ElevatedButton(
                "📁 Выбрать из галереи",
                on_click=lambda e: file_picker.pick_files(
                    allowed_extensions=["jpg", "jpeg", "png", "gif", "bmp"],
                    allow_multiple=True
                ),
                style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.BLUE),
                icon=ft.icons.PHOTO_LIBRARY
            ),
            ft.ElevatedButton(
                "📷 Сделать фото",
                on_click=take_photo,
                style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.GREEN),
                icon=ft.icons.CAMERA_ALT
            ),
        ]),
        ft.Container(height=5),
        ft.Text("Выбранные файлы:", size=12, color=ft.Colors.GREY),
        ft.Container(
            content=files_list_view,
            border=ft.border.all(1, ft.Colors.GREY_400),
            border_radius=5,
            padding=10,
            width=400,
            min_height=50
        ),
        ft.Text("(поддерживаются JPG, PNG, GIF, BMP)", size=10, color=ft.Colors.GREY)
    ])
    
    # Поле для ввода текста
    text_field = ft.TextField(
        label="Примечание",
        hint_text="Введите текст (будет сохранено в поле f17560)",
        width=400,
        multiline=True,
        min_lines=3,
        max_lines=5
    )
    
    # Статус сообщение
    status_label = ft.Text("", color=ft.Colors.GREY)
    
    # Загружаем записи
    records_list, dropdown_options = load_records()
    
    # Обработчик изменения выбранной записи
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
        
        page.update()
    
    # Создаем выпадающий список
    records_dropdown = ft.Dropdown(
        label="Выберите запись",
        hint_text="Выберите запись из списка",
        width=400,
        options=dropdown_options,
        on_change=on_record_change,
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
        selected_files.clear()
        files_list_view.controls.clear()
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
        
        headers = {
            "Content-Type": "application/vnd.api+json",
            "X-Auth-Token": TOKEN
        }
        
        payload = {
            "data": {
                "type": "data160",
                "id": selected_record_id,
                "attributes": {}
            }
        }
        
        if user_text:
            payload["data"]["attributes"]["f17560"] = user_text
        
        if selected_files:
            photos_list = []
            for file_path in selected_files:
                try:
                    with open(file_path, "rb") as f:
                        image_data = base64.b64encode(f.read()).decode('utf-8')
                    
                    file_obj = {
                        "file_name": os.path.basename(file_path),
                        "content": image_data,
                        "binary": True
                    }
                    photos_list.append(file_obj)
                except Exception as img_err:
                    status_label.value = f"❌ Ошибка чтения фото: {str(img_err)}"
                    status_label.color = ft.Colors.RED
                    page.update()
                    return
            
            if photos_list:
                if len(photos_list) == 1:
                    payload["data"]["attributes"]["f17540"] = photos_list[0]
                else:
                    payload["data"]["attributes"]["f17540"] = photos_list
        
        if not user_text and not selected_files:
            status_label.value = "❌ Введите текст или выберите фото"
            status_label.color = ft.Colors.RED
            page.update()
            return
        
        status_label.value = "⏳ Отправка..."
        status_label.color = ft.Colors.BLUE
        page.update()
        
        try:
            response = requests.patch(API_URL, headers=headers, json=payload)
            
            if response.status_code == 200:
                success_parts = []
                if user_text:
                    success_parts.append(f"текст '{user_text}'")
                if selected_files:
                    success_parts.append(f"{len(selected_files)} фото")
                
                success_msg = f"✅ {', '.join(success_parts)} успешно сохранено в записи {selected_record_id}"
                
                dialog.content = ft.Text(success_msg, size=16, text_align=ft.TextAlign.CENTER)
                page.overlay.append(dialog)
                dialog.open = True
                text_field.value = ""
                selected_files.clear()
                files_list_view.controls.clear()
                status_label.value = ""
                page.update()
            else:
                status_label.value = f"❌ Ошибка {response.status_code}: {response.text[:200]}"
                status_label.color = ft.Colors.RED
                page.update()
        except Exception as err:
            status_label.value = f"❌ Ошибка соединения: {str(err)}"
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
                ft.Text("Изменение примечания и фото", size=24, weight=ft.FontWeight.BOLD),
                ft.Divider(height=20),
                records_dropdown,
                ft.Container(height=20),
                photos_section,
                ft.Container(height=15),
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