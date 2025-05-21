import customtkinter as ctk
from tkcalendar import DateEntry
from tkinter import ttk
import json
from datetime import datetime, timedelta
import threading
import time
from tkinter import messagebox
import random
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image

class StudentDayApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("День студента 25")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        self.icon_path = "icon.ico"  
        self.current_user = None
        self.data_file = 'data.json'
        self.session_file = 'session.json'
        self.config_file = 'config.json' 
        self.load_data()
        self.load_config()
        ctk.set_appearance_mode(self.config.get("theme", "Dark"))
        self.load_session()

    def set_window_icon(self, window):
        try:
            window.iconbitmap(self.icon_path)
        except Exception as e:
            print(f"Ошибка загрузки иконки: {e}")

    def load_data(self):
        try:
            with open(self.data_file, 'r') as file:
                self.data = json.load(file)
        except FileNotFoundError:
            self.data = {"users": [], "tasks": []}
            self.save_data()


    def save_data(self):
        with open(self.data_file, 'w') as file:
            json.dump(self.data, file, indent=4)

    def load_config(self):
        try:
            with open(self.config_file, 'r') as file:
                self.config = json.load(file)
        except FileNotFoundError:
            self.config = {"theme": "Dark"}
            self.save_config()

    def save_config(self):
        with open(self.config_file, 'w') as file:
            json.dump(self.config, file, indent=4)

    def load_session(self):
        try:
            with open(self.session_file, 'r') as file:
                session = json.load(file)
                if session.get("username"):
                    self.current_user = session["username"]
                    self.show_main_window()
                    return
        except FileNotFoundError:
            self.clear_session()
            self.show_login_window()

    def save_session(self):
        with open(self.session_file, 'w') as file:
            json.dump({"username": self.current_user}, file)

    def clear_session(self):
        self.current_user = None
        try:
            with open(self.session_file, 'w') as file:
                json.dump({}, file)
        except FileNotFoundError:
            # Если файл не существует, создаем его
            with open(self.session_file, 'w') as file:
                json.dump({}, file)
        self.show_login_window()

    def load_user(self, username):
        for user in self.data["users"]:
            if user["username"] == username:
                return user["id"]
        return None

    def load_tasks(self, filter_completed=None):
        if not self.current_user:
            return []
        user_id = self.load_user(self.current_user)
        tasks = [task for task in self.data["tasks"] if task["user_id"] == user_id]
        if filter_completed is not None:
            tasks = [task for task in tasks if task["completed"] == filter_completed]
        return tasks

    def save_task(self, task):
        user_id = self.load_user(self.current_user)
        task["id"] = len(self.data["tasks"]) + 1
        task["user_id"] = user_id
        self.data["tasks"].append(task)
        self.save_data()

    def update_task(self, task_id, field, value):
        for task in self.data["tasks"]:
            if task["id"] == task_id:
                task[field] = value
                self.save_data()
                return

    def delete_task(self, task_id):
        self.data["tasks"] = [task for task in self.data["tasks"] if task["id"] != task_id]
        self.save_data()

    def show_login_window(self):
        self.login_frame = ctk.CTkFrame(self.root, corner_radius=15)
        self.login_frame.place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(self.login_frame, text="Добро пожаловать!", font=("Arial Bold", 24)).grid(row=0, column=0, columnspan=2, pady=20)
        ctk.CTkLabel(self.login_frame, text="Логин:").grid(row=1, column=0, padx=10, pady=5)
        self.username_entry = ctk.CTkEntry(self.login_frame, width=200)
        self.username_entry.grid(row=1, column=1, padx=10, pady=5)
        ctk.CTkLabel(self.login_frame, text="Пароль:").grid(row=2, column=0, padx=10, pady=5)
        self.password_entry = ctk.CTkEntry(self.login_frame, show="*", width=200)
        self.password_entry.grid(row=2, column=1, padx=10, pady=5)
        login_btn = ctk.CTkButton(self.login_frame, text="Войти", command=self.login, fg_color="#2E8B57", hover_color="#3CB371")
        login_btn.grid(row=3, column=0, columnspan=2, pady=20, padx=10, sticky="ew")
        register_btn = ctk.CTkButton(self.login_frame, text="Регистрация", command=self.register, fg_color="#1E90FF", hover_color="#4169E1")
        register_btn.grid(row=4, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if not username or not password:
            messagebox.showerror("Ошибка", "Заполните все поля")
            return
        user = next((u for u in self.data["users"] if u["username"] == username and u["password"] == password), None)
        if user:
            self.current_user = username
            self.save_session()
            self.login_frame.destroy()
            self.show_main_window()
        else:
            messagebox.showerror("Ошибка", "Неверные данные")

    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if not username or not password:
            messagebox.showerror("Ошибка", "Заполните все поля")
            return
        if any(user["username"] == username for user in self.data["users"]):
            messagebox.showerror("Ошибка", "Имя пользователя занято")
            return
        self.data["users"].append({"id": len(self.data["users"]) + 1, "username": username, "password": password})
        self.save_data()
        messagebox.showinfo("Успех", "Регистрация успешна")
        self.login_frame.destroy()
        self.show_login_window()

    def show_main_window(self):
        self.sidebar = ctk.CTkFrame(self.root, width=200, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        ctk.CTkButton(self.sidebar, text="Главная", command=self.show_dashboard, fg_color="transparent", corner_radius=0, hover_color="#2F4F4F").pack(fill="x")
        ctk.CTkButton(self.sidebar, text="+ Новая задача", command=self.add_task_window, fg_color="#483D8B", hover_color="#6A5ACD").pack(fill="x", pady=5)
        ctk.CTkButton(self.sidebar, text="Статистика", command=self.show_statistics, fg_color="#FFA500", hover_color="#FF8C00").pack(fill="x", pady=5)
        ctk.CTkButton(self.sidebar, text="Сменить тему", command=self.toggle_theme, fg_color="#800080", hover_color="#9932CC").pack(fill="x", pady=5)
        ctk.CTkButton(self.sidebar, text="Выйти", command=self.logout, fg_color="#DC143C", hover_color="#B22222").pack(fill="x", pady=5)
        self.main_content = ctk.CTkFrame(self.root)
        self.main_content.pack(side="right", fill="both", expand=True, padx=20, pady=20)
        self.show_dashboard()

    def logout(self):
        self.clear_session()
        self.sidebar.destroy()
        self.main_content.destroy()

    def toggle_theme(self):
        current_mode = ctk.get_appearance_mode()
        new_mode = "Light" if current_mode == "Dark" else "Dark"
        ctk.set_appearance_mode(new_mode)
        self.config["theme"] = new_mode
        self.save_config()

    def show_dashboard(self):
        for widget in self.main_content.winfo_children():
            widget.destroy()
        quotes = [
            "Верьте в себя и все получится.",
            "Каждый день — это новая возможность.",
            "Маленькие шаги приводят к большим изменениям."
        ]
        quote_label = ctk.CTkLabel(self.main_content, text=random.choice(quotes), font=("Arial Italic", 14))
        quote_label.pack(pady=10)
        greeting = f"Доброе утро, {self.current_user}!" if datetime.now().hour < 12 else f"Добрый день, {self.current_user}!"
        ctk.CTkLabel(self.main_content, text=greeting, font=("Arial Bold", 18)).pack(pady=10)
        search_frame = ctk.CTkFrame(self.main_content)
        search_frame.pack(fill="x", pady=10)
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Поиск задач...", width=300)
        self.search_entry.pack(side="left", padx=10)
        self.search_entry.bind("<KeyRelease>", self.search_tasks)
        filter_frame = ctk.CTkFrame(search_frame, fg_color="transparent")
        filter_frame.pack(side="right", padx=10)
        ctk.CTkButton(filter_frame, text="Активные задачи", command=lambda: self.refresh_tasks(filter_completed=False),
                     fg_color="#4CAF50", hover_color="#45a049").pack(side="left", padx=5)
        ctk.CTkButton(filter_frame, text="Завершенные задачи", command=lambda: self.refresh_tasks(filter_completed=True),
                     fg_color="#FF9800", hover_color="#FFA726").pack(side="left", padx=5)
        self.tasks_container = ctk.CTkScrollableFrame(self.main_content)
        self.tasks_container.pack(fill="both", expand=True)
        self.refresh_tasks()

    def refresh_tasks(self, filter_completed=None):
        for widget in self.tasks_container.winfo_children():
            widget.destroy()
        loading_label = ctk.CTkLabel(self.tasks_container, text="Загрузка задач...", font=("Arial Bold", 14))
        loading_label.pack(pady=20)
        self.root.update_idletasks()
        time.sleep(0.5)  # Имитация задержки
        loading_label.destroy()
        search_query = self.search_entry.get().lower()
        tasks = self.load_tasks(filter_completed=filter_completed)
        filtered = [t for t in tasks 
                   if search_query in t['title'].lower() or 
                   search_query in t['description'].lower()]
        for task in filtered:
            task_frame = ctk.CTkFrame(self.tasks_container, 
                                     fg_color=self.get_priority_color(task['priority']),
                                     corner_radius=10)
            task_frame.pack(fill="x", pady=5, padx=10)
            header = ctk.CTkFrame(task_frame, fg_color="transparent")
            header.pack(fill="x", pady=5)
            ctk.CTkLabel(header, text=task['title'], 
                        font=("Arial Bold", 16), 
                        text_color=self.get_priority_text_color(task['priority'])).pack(side="left", padx=10)
            ctk.CTkLabel(header, text=task['priority'], 
                        text_color=self.get_priority_text_color(task['priority']), 
                        font=("Arial Italic", 12)).pack(side="right", padx=10)
            ctk.CTkLabel(task_frame, text=f"Дата: {task['date']} {task['time']}", 
                        text_color=self.get_priority_text_color(task['priority'])).pack(anchor="w", padx=10)
            ctk.CTkLabel(task_frame, text=task['description'], 
                        text_color=self.get_priority_text_color(task['priority'])).pack(anchor="w", padx=10, pady=(0,5))
            actions = ctk.CTkFrame(task_frame, fg_color="transparent")
            actions.pack(fill="x", pady=5)
            ctk.CTkButton(actions, text="✅ Выполнено", 
                         command=lambda t=task: self.complete_task(t),
                         fg_color="green", hover_color="#228B22",
                         width=100).pack(side="left", padx=10)
            ctk.CTkButton(actions, text="🗑️ Удалить", 
                         command=lambda t=task: self.delete_task_ui(t),
                         fg_color="#DC143C", hover_color="#B22222",
                         width=100).pack(side="right", padx=10)

    def get_priority_color(self, priority):
        return {
            "Высокий": "#FF4500",
            "Средний": "#FFA500",
            "Низкий": "#32CD32"
        }[priority]

    def get_priority_text_color(self, priority):
        return {
            "Высокий": "#FFFFFF",
            "Средний": "#000000",
            "Низкий": "#000000"
        }[priority]

    def add_task_window(self):
        window = ctk.CTkToplevel()
        window.title("Создать задачу")
        window.geometry("500x600")
        self.set_window_icon(window)  
        ctk.CTkLabel(window, text="Название:", font=("Arial Bold", 14)).pack(pady=5)
        title = ctk.CTkEntry(window, width=400)
        title.pack(pady=5)
        ctk.CTkLabel(window, text="Описание:", font=("Arial Bold", 14)).pack(pady=5)
        description = ctk.CTkTextbox(window, height=150)
        description.pack(pady=5)
        ctk.CTkLabel(window, text="Приоритет:", font=("Arial Bold", 14)).pack(pady=5)
        priority = ctk.CTkOptionMenu(window, values=["Высокий", "Средний", "Низкий"], fg_color="#483D8B", button_color="#6A5ACD")
        priority.pack(pady=5)
        datetime_frame = ctk.CTkFrame(window)
        datetime_frame.pack(pady=10)
        ctk.CTkLabel(datetime_frame, text="Дата:").pack(side="left", padx=10)
        date_picker = DateEntry(datetime_frame, date_pattern='yyyy-mm-dd')
        date_picker.pack(side="left", padx=10)
        ctk.CTkLabel(datetime_frame, text="Время:").pack(side="left", padx=10)
        time_frame = ctk.CTkFrame(datetime_frame, fg_color="transparent")
        time_frame.pack(side="left", padx=10)
        hours = ttk.Spinbox(time_frame, from_=0, to=23, width=5)
        hours.pack(side="left")
        hours.set("12")
        ctk.CTkLabel(time_frame, text=":").pack(side="left")
        minutes = ttk.Spinbox(time_frame, from_=0, to=59, width=5)
        minutes.pack(side="left")
        minutes.set("00")
        def save_task():
            new_task = {
                "title": title.get(),
                "description": description.get("1.0", "end").strip(),
                "priority": priority.get(),
                "date": date_picker.get(),
                "time": f"{hours.get().zfill(2)}:{minutes.get().zfill(2)}",
                "completed": False
            }
            self.save_task(new_task)
            self.refresh_tasks()
            window.destroy()
        save_btn = ctk.CTkButton(window, text="Создать задачу", command=save_task, fg_color="#4CAF50", hover_color="#45a049")
        save_btn.pack(pady=20)

    def search_tasks(self, event=None):
        self.refresh_tasks()

    def complete_task(self, task):
        self.update_task(task["id"], "completed", True)
        self.refresh_tasks()

    def delete_task_ui(self, task):
        if messagebox.askyesno("Удаление", "Удалить задачу?"):
            self.delete_task(task["id"])
            self.refresh_tasks()

    def show_statistics(self):
        tasks = self.load_tasks()
        total = len(tasks)
        completed = sum(1 for task in tasks if task["completed"])
        pending = total - completed
        stats_window = ctk.CTkToplevel()
        stats_window.title("Статистика")
        stats_window.geometry("600x400")
        fig, ax = plt.subplots(figsize=(5, 3))
        labels = ['Выполнено', 'В процессе']
        sizes = [completed, pending]
        colors = ['#4CAF50', '#FF9800']
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
        ax.axis('equal')
        canvas = FigureCanvasTkAgg(fig, master=stats_window)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill="both", expand=True)
        canvas.draw()

    def check_reminders(self):
        def check():
            while True:
                now = datetime.now()
                soon = now + timedelta(minutes=10)
                current_time = now.strftime("%H:%M")
                current_date = now.strftime("%Y-%m-%d")
                soon_time = soon.strftime("%H:%M")
                soon_date = soon.strftime("%Y-%m-%d")
                for task in self.load_tasks():
                    if not task["completed"]:
                        if task["date"] == current_date and task["time"] == current_time:
                            self.show_notification(task)
                            self.update_task(task["id"], "completed", True)
                        elif task["date"] == soon_date and task["time"] == soon_time:
                            self.show_notification(task, soon=True)
                time.sleep(60)
        thread = threading.Thread(target=check, daemon=True)
        thread.start()

    def show_notification(self, task, soon=False):
        message = f"Задача: {task['title']}\n{task['description']}\nВремя: {task['date']} {task['time']}"
        if soon:
            message = "Скоро начнется:\n" + message
        messagebox.showinfo("Напоминание", message)

if __name__ == "__main__":
    app = StudentDayApp()
    app.check_reminders()
    app.root.mainloop()