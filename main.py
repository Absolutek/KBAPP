import flet as ft
import requests
import base64
import os

TOKEN = "vhd0WTv1bqvn9dnYomoY9ye9aFLXcaiJLrdshigxKReJJha6"
API_URL = "https://cb-test.jsdf.ru/api/dev/data160/1547"

def main(page: ft.Page):
    page.title = "Загрузка фото"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    selected_file_path = None
    selected_file_name = None
    file_info_text = ft.Text("Файл не выбран", size=12, color=ft.Colors.GREY)
    status_label = ft.Text("", size=14)

    def on_file_picked(e):
        nonlocal selected_file_path, selected_file_name
        if e.files:
            selected_file_path = e.files[0].path
            selected_file_name = e.files[0].name
            file_info_text.value = f"✅ Выбран: {selected_file_name}"
            file_info_text.color = ft.Colors.GREEN
            status_label.value = ""
            page.update()
    
    file_picker = ft.FilePicker()
    file_picker.on_result = on_file_picked
    page.overlay.append(file_picker)
    
    select_button = ft.ElevatedButton(
        "📁 Выбрать фото",
        on_click=lambda _: file_picker.pick_files(allow_multiple=False)
    )
    
    def send_photo(e):
        nonlocal selected_file_path, selected_file_name
        if not selected_file_path:
            status_label.value = "❌ Выберите фото"
            status_label.color = ft.Colors.RED
            page.update()
            return
        
        status_label.value = "⏳ Отправка..."
        status_label.color = ft.Colors.BLUE
        page.update()
        
        try:
            with open(selected_file_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
            
            payload = {
                "data": {
                    "type": "data160",
                    "id": "1547",
                    "attributes": {
                        "f17550": {
                            "file_name": selected_file_name,
                            "content": image_data,
                            "binary": True
                        }
                    }
                }
            }
            
            response = requests.patch(
                API_URL,
                headers={"Content-Type": "application/vnd.api+json", "X-Auth-Token": TOKEN},
                json=payload
            )
            
            if response.status_code == 200:
                status_label.value = "✅ Отправлено!"
                status_label.color = ft.Colors.GREEN
                selected_file_path = None
                selected_file_name = None
                file_info_text.value = "Файл не выбран"
                file_info_text.color = ft.Colors.GREY
            else:
                status_label.value = f"❌ Ошибка {response.status_code}"
                status_label.color = ft.Colors.RED
        except Exception as err:
            status_label.value = f"❌ {err}"
            status_label.color = ft.Colors.RED
        page.update()
    
    send_button = ft.ElevatedButton("📤 Отправить", on_click=send_photo)
    
    page.add(
        ft.Column(
            [
                ft.Text("Загрузка фото", size=24, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                select_button,
                file_info_text,
                send_button,
                status_label
            ],
            spacing=20,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    )

if __name__ == "__main__":
    ft.app(target=main)