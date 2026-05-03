import flet as ft
import requests

API_URL = "https://cb-test.jsdf.ru/api/dev/data160/1547"
TOKEN = "vhd0WTv1bqvn9dnYomoY9ye9aFLXcaiJLrdshigxKReJJha6"

def main(page: ft.Page):
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
        user_text = text_field.value.strip()
        
        if not user_text:
            status_label.value = "❌ Введите текст перед отправкой"
            status_label.color = ft.Colors.RED
            page.update()
            return
        
        # Формируем запрос
        headers = {
            "Content-Type": "application/vnd.api+json",
            "X-Auth-Token": TOKEN
        }
        
        payload = {
            "data": {
                "type": "data160",
                "id": "1547",
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
                # Обновляем содержимое диалога
                dialog.content = ft.Text(
                    f"Значение '{user_text}' успешно сохранено в поле f17560",
                    size=16,
                    text_align=ft.TextAlign.CENTER
                )
                # Показываем диалог
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
        style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.BLUE)
    )
    
    # Добавляем элементы на страницу
    page.add(
        ft.Column(
            [
                ft.Text("Изменение поля f17560", size=24, weight=ft.FontWeight.BOLD),
                ft.Divider(height=20),
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

ft.app(target=main)