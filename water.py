import customtkinter as ctk
import json
from datetime import datetime, timedelta
import threading
import time
import pygame
import os
from PIL import Image, ImageDraw
import pystray
import ctypes
import sys
import tkinter as tk

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join("user_data.json")
SETTINGS_FILE = os.path.join("settings.json")
SOUND_FOLDER = os.path.join("sound")
ICON_PATH = os.path.join("icons", "icon.ico")
SETTINGS_ICON_PATH = os.path.join("icons", "settings_icon.ico")
REMINDER_ICON_PATH = os.path.join("icons", "reminder_icon.ico")

THEMES = {
    "Современность": {"primary": "#2A3138", "secondary": "#3DB389", "text": "#F5F5F5", "button_fg": "#3DB389", "button_hover": "#2E7D32", "accent": "#FF6B6B"},
    "Классика": {"primary": "#7A3E11", "secondary": "#D2B48C", "text": "#FFF8E1", "button_fg": "#D2B48C", "button_hover": "#B8860B", "accent": "#A0522D"},
    "Ретро": {"primary": "#E63946", "secondary": "#FF8C69", "text": "#FFFFFF", "button_fg": "#FF8C69", "button_hover": "#E63946", "accent": "#FFD166"},
    "Будущее": {"primary": "#0A0A12", "secondary": "#00F5FF", "text": "#FFFFFF", "button_fg": "#00F5FF", "button_hover": "#00B4BF", "accent": "#FF00F5"},
    "Минимализм": {"primary": "#FFFFFF", "secondary": "#F0F0F0", "text": "#333333", "button_fg": "#DDDDDD", "button_hover": "#CCCCCC", "accent": "#555555"},
    "Тёмная": {"primary": "#121212", "secondary": "#333333", "text": "#E0E0E0", "button_fg": "#444444", "button_hover": "#555555", "accent": "#BB86FC"},
    "Природа": {"primary": "#2E5E3D", "secondary": "#7CB083", "text": "#FFFFFF", "button_fg": "#7CB083", "button_hover": "#4A7856", "accent": "#F4D35E"},
    "Пастель": {"primary": "#FFD6E0", "secondary": "#C1E7FF", "text": "#333333", "button_fg": "#C1E7FF", "button_hover": "#A5D5F7", "accent": "#B5EAD7"},
    "Базовый": {"primary": "#F5F5F5", "secondary": "#D3D3D3", "text": "#000000", "button_fg": "#D3D3D3", "button_hover": "#A9A9A9"}
}

def load_data(file_path):
    try:
        if not os.path.exists(file_path):
            return {}
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Ошибка загрузки {file_path}: {str(e)}")
        return {}

def save_data(file_path, data):
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Ошибка сохранения {file_path}: {str(e)}")

def create_default_files():
    if not os.path.exists(DATA_FILE):
        default_user_data = {
            "Гость": {"daily_goal": 2000, "consumed": 0, "gender": "unknown"},
            "user1": {"password": "password123", "daily_goal": 3700, "consumed": 0, "gender": "male"},
            "user2": {"password": "securepass", "daily_goal": 2700, "consumed": 0, "gender": "female"}
        }
        save_data(DATA_FILE, default_user_data)
    if not os.path.exists(SETTINGS_FILE):
        default_settings = {
            "appearance_mode": "Light",
            "sound_enabled": True,
            "selected_sound": "sound1.mp3",
            "reminder_interval_hours": 1,
            "reminder_interval_minutes": 0,
            "reminder_interval_seconds": 0,
            "last_logged_in_user": None,
            "theme_color": "Базовый",
            "reset_time": "00:00",
            "daily_base_male": 3700,
            "daily_base_female": 2700,
            "interval_male": 45 * 60,
            "interval_female": 60 * 60
        }
        save_data(SETTINGS_FILE, default_settings)
    for sound in ["sound1.mp3", "sound2.mp3", "sound3.mp3", "sound4.mp3", "sound5.mp3"]:
        sound_path = os.path.join(SOUND_FOLDER, sound)
        if not os.path.exists(sound_path):
            try:
                with open(sound_path, "wb") as f:
                    pass  
            except Exception as e:
                print(f"Не удалось создать файл {sound}: {str(e)}")

class NavigationHandler:
    def __init__(self, app):
        self.app = app
        self.app.bind("<Escape>", self.handle_escape)

    def handle_escape(self, event):
        if self.has_active_frame('register_frame'):
            self.app.show_login_content()
            return "break"
        if self.has_active_frame('login_frame'):
            self.app.show_main_content()
            return "break"

    def has_active_frame(self, frame_name):
        frame = getattr(self.app, frame_name, None)
        return frame and frame.winfo_ismapped()

class AppManager:
    def __init__(self, root):
        self.root = root
        self.tray_icon = None
        self.is_hidden = False
        self.setup_close_handler()
        self.create_tray_icon()

    def setup_close_handler(self):
        self.root.protocol("WM_DELETE_WINDOW", self.hide_to_tray)
        if sys.platform == "win32":
            self.root.update_idletasks()

    def hide_to_tray(self):
        self.is_hidden = True
        self.root.withdraw()
        self.root.update_idletasks()

    def show_from_tray(self):
        self.is_hidden = False
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
        self.root.attributes('-topmost', True)
        self.root.after(100, lambda: self.root.attributes('-topmost', False))

    def create_tray_icon(self):
        image = Image.open(ICON_PATH) if os.path.exists(ICON_PATH) else Image.new('RGB', (64, 64), '#4CAF50')
        menu = (
            pystray.MenuItem('Открыть', self.show_from_tray),
            pystray.MenuItem('Выход', self.exit_app)
        )
        self.tray_icon = pystray.Icon("water_app", image, "Водяной", menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def exit_app(self, icon=None, item=None):
        self.tray_icon.stop()
        self.root.destroy()
        os._exit(0)

class WaterApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.app_manager = AppManager(self)
        self.nav_handler = NavigationHandler(self)
        self.title("Водяной")
        self.geometry("500x900")
        self.resizable(False, False)
        self.setup_icon()
        self.current_user = None
        self.reminder_active = False
        self.reminder_lock = threading.Lock()
        self.user_data = load_data(DATA_FILE)
        self.settings = load_data(SETTINGS_FILE)
        self.current_user = self.settings.get("last_logged_in_user", None)
        pygame.mixer.init()
        self.sounds = {
            "sound1": os.path.join(SOUND_FOLDER, "sound1.mp3"),
            "sound2": os.path.join(SOUND_FOLDER, "sound2.mp3"),
            "sound3": os.path.join(SOUND_FOLDER, "sound3.mp3"),
            "sound4": os.path.join(SOUND_FOLDER, "sound4.mp3"),
            "sound5": os.path.join(SOUND_FOLDER, "sound5.mp3")
        }
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True)
        # Start with registration screen instead of guest login
        self.show_registration_screen()
        self.apply_settings()
        self.start_background_threads()
        self.current_user = self.settings.get("last_logged_in_user", None)
        if self.current_user and self.current_user in self.user_data and self.current_user != "Гость":
            self.show_main_content()
        else:
            self.show_welcome_screen() 
        try:
            pygame.mixer.init()
        except pygame.error:
            print("Ошибка инициализации звука. Звук будет отключен.")
            self.settings["sound_enabled"] = False  # Отключаем звук в настройках
            save_data(SETTINGS_FILE, self.settings)

    def show_welcome_screen(self):
        self.clear_window()
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True)
        
        title_label = ctk.CTkLabel(
            main_frame,
            text="Добро пожаловать!",
            font=("Arial", 24, "bold"),
            text_color="#4CAF50"
        )
        title_label.place(relx=0.5, rely=0.3, anchor="center")
        
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        login_button = ctk.CTkButton(
            buttons_frame,
            text="Войти",
            command=self.show_login_content,
            corner_radius=15,
            font=("Arial", 16, "bold"),
            width=200,
            height=40
        )
        login_button.pack(pady=15, fill="x")
        
        register_button = ctk.CTkButton(
            buttons_frame,
            text="Зарегистрироваться",
            command=self.register,
            corner_radius=15,
            font=("Arial", 16, "bold"),
            width=200,
            height=40
        )
        register_button.pack(pady=15, fill="x")
        
        self.update_widget_styles(main_frame)

    # Новый метод для отображения формы входа
    def show_login_content(self):
        self.clear_window()
        self.login_frame = ctk.CTkFrame(self)
        self.login_frame.pack(fill="both", expand=True)
        
        ctk.CTkLabel(self.login_frame, text="Вход", font=("Arial", 20, "bold")).pack(pady=12, padx=10)
        
        self.username_entry = ctk.CTkEntry(self.login_frame, placeholder_text="Логин")
        self.username_entry.pack(pady=12, padx=10)
        
        self.password_entry = ctk.CTkEntry(self.login_frame, placeholder_text="Пароль", show="*")
        self.password_entry.pack(pady=12, padx=10)
        
        self.error_label = ctk.CTkLabel(self.login_frame, text="", text_color="red")
        self.error_label.pack(pady=10)
        
        login_button = ctk.CTkButton(
            self.login_frame,
            text="Войти",
            command=self.attempt_login,
            corner_radius=15,
            font=("Arial", 16, "bold")
        )
        login_button.pack(pady=12, padx=10)
        
        back_button = ctk.CTkButton(
            self.login_frame,
            text="Назад",
            command=self.show_welcome_screen,
            corner_radius=15,
            font=("Arial", 16, "bold")
        )
        back_button.pack(pady=10, padx=10)
        
        self.update_widget_styles(self.login_frame)

    def attempt_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if username in self.user_data:
            stored_password = self.user_data[username].get("password", "")
            if stored_password == password:
                self.current_user = username
                self.settings["last_logged_in_user"] = username
                save_data(SETTINGS_FILE, self.settings)
                self.show_main_content()
                return
                
        self.error_label.configure(text="Неверный логин или пароль")

    def register(self):
        self.clear_window()
        self.register_frame = ctk.CTkFrame(self)
        self.register_frame.pack(fill="both", expand=True)
        
        ctk.CTkLabel(self, text="Регистрация", font=("Arial", 20, "bold")).pack(pady=12, padx=10)
        
        username_entry = ctk.CTkEntry(self, placeholder_text="Логин")
        username_entry.pack(pady=12, padx=10)
        
        password_entry = ctk.CTkEntry(self, placeholder_text="Пароль", show="*")
        password_entry.pack(pady=12, padx=10)
        
        gender_var = ctk.StringVar(value="male")
        gender_frame = ctk.CTkFrame(self, fg_color="transparent")
        gender_frame.pack(pady=10)
        
        ctk.CTkRadioButton(gender_frame, text="Мужской", variable=gender_var, value="male").pack(side="left", padx=10)
        ctk.CTkRadioButton(gender_frame, text="Женский", variable=gender_var, value="female").pack(side="left", padx=10)
        
        def complete_registration():
            username = username_entry.get()
            password = password_entry.get()
            gender = gender_var.get()
            
            if not username or not password:
                self.error_label.configure(text="Логин и пароль не могут быть пустыми")
                return
                
            if username in self.user_data:
                self.error_label.configure(text="Пользователь уже существует")
                return
                
            daily_goal = 3700 if gender == "male" else 2700
            self.user_data[username] = {
                "password": password,
                "daily_goal": daily_goal,
                "consumed": 0,
                "gender": gender
            }
            
            save_data(DATA_FILE, self.user_data)
            self.current_user = username
            self.settings["last_logged_in_user"] = username
            save_data(SETTINGS_FILE, self.settings)
            
            self.error_label.configure(text="Регистрация успешна!", text_color="green")
            self.show_main_content()
            
        register_button = ctk.CTkButton(
            self,
            text="Зарегистрироваться",
            command=complete_registration,
            corner_radius=15,
            font=("Arial", 16, "bold")
        )
        register_button.pack(pady=12, padx=10)
        
        self.error_label = ctk.CTkLabel(self, text="", text_color="red")
        self.error_label.pack(pady=10)

    def logout(self):
        self.settings["last_logged_in_user"] = None 
        save_data(SETTINGS_FILE, self.settings)
        self.current_user = None
        self.show_welcome_screen()


    def setup_icon(self):
        if os.path.exists(ICON_PATH):
            try:
               self.iconbitmap(ICON_PATH)
               return  
            except Exception as e:
               print(f"Ошибка загрузки .ico иконки: {e}")
        png_path = os.path.join(os.path.dirname(ICON_PATH), "icon.png")
        if os.path.exists(png_path):
            try:
                img = tk.PhotoImage(file=png_path)
                self.tk.call('wm', 'iconphoto', self._w, img)
                return 
            except Exception as e:
                print(f"Ошибка загрузки .png иконки: {e}")
        print("Иконка не найдена. Будет использована стандартная иконка системы.")

    def create_temp_icon(self):
        img = Image.new('RGB', (32, 32), '#4CAF50')
        temp_path = os.path.join(CURRENT_DIR, "temp_icon.ico")
        img.save(temp_path)
        self.iconbitmap(temp_path)

    def apply_settings(self):
        appearance_mode = self.settings.get("appearance_mode", "Light")
        theme_color = self.settings.get("theme_color", "Базовый")
        theme = THEMES.get(theme_color, THEMES["Базовый"])
        ctk.set_appearance_mode(appearance_mode)
        self.configure(fg_color=theme["primary"])
        self.update_widget_styles(self)

    def update_widget_styles(self, widget):
        theme = THEMES.get(self.settings.get("theme_color", "Базовый"), THEMES["Базовый"])
        for child in widget.winfo_children():
            if isinstance(child, ctk.CTkLabel):
                child.configure(text_color=theme["text"])
            elif isinstance(child, ctk.CTkProgressBar):
                child.configure(progress_color=theme["secondary"])
            elif isinstance(child, ctk.CTkButton):
                child.configure(
                    fg_color=theme["button_fg"],
                    hover_color=theme["button_hover"]
                )
            elif isinstance(child, ctk.CTkFrame):
                child.configure(fg_color=theme["primary"])
                self.update_widget_styles(child)
        if isinstance(widget, (ctk.CTk, ctk.CTkToplevel)):
            widget.configure(fg_color=theme["primary"])

    def start_background_threads(self):
        self.reminder_thread = threading.Thread(target=self.reminder, daemon=True)
        self.reminder_thread.start()
        self.reset_thread = threading.Thread(target=self.daily_reset, daemon=True)
        self.reset_thread.start()

    def reminder(self):
        while True:
            hours = self.settings.get("reminder_interval_hours", 1)
            minutes = self.settings.get("reminder_interval_minutes", 0)
            seconds = self.settings.get("reminder_interval_seconds", 0)
            total_seconds = hours * 3600 + minutes * 60 + seconds
            with self.reminder_lock:
                if self.reminder_active or self.check_progress_completed() or total_seconds == 0:
                    time.sleep(1)
                    continue
            time.sleep(total_seconds)
            if self.settings.get("sound_enabled", True):
                self.show_reminder_window()

    def check_progress_completed(self):
        if not self.current_user or self.current_user not in self.user_data:
            return False
        goal = self.user_data[self.current_user].get("daily_goal", 0)
        consumed = self.user_data[self.current_user].get("consumed", 0)
        return goal > 0 and consumed >= goal

    def show_reminder_window(self):
        with self.reminder_lock:
            if self.check_progress_completed():
                return
            self.reminder_active = True
        reminder_window = ctk.CTkToplevel(self)
        reminder_window.title("Напоминание")
        reminder_window.geometry("300x200")
        reminder_window.attributes("-topmost", True)
        reminder_window.resizable(False, False)
        sound_path = self.sounds.get(self.settings.get("selected_sound", "sound1"))
        if sound_path and os.path.exists(sound_path):
            pygame.mixer.music.load(sound_path)
            pygame.mixer.music.play(-1)
        def close_reminder():
            pygame.mixer.music.stop()
            with self.reminder_lock:
                self.reminder_active = False
            self.add_water(250)
            reminder_window.destroy()
        ctk.CTkLabel(reminder_window, text="Пора выпить воды!", font=("Arial", 20, "bold")).pack(pady=20)
        ok_button = ctk.CTkButton(
            reminder_window,
            text="OK",
            command=close_reminder,
            corner_radius=15,
            font=("Arial", 16, "bold")
        )
        ok_button.pack(pady=10, ipadx=20, ipady=5)
        self.update_widget_styles(reminder_window)

    def daily_reset(self):
        while True:
            now = datetime.now()
            reset_time = datetime.strptime(self.settings.get("reset_time", "00:00"), "%H:%M").time()
            next_reset = datetime.combine(now.date(), reset_time)
            if now.time() > reset_time:
                next_reset += timedelta(days=1)
            time_to_wait = (next_reset - now).total_seconds()
            time.sleep(time_to_wait)
            for user in self.user_data:
                self.user_data[user]["consumed"] = 0
            save_data(DATA_FILE, self.user_data)
            if self.current_user:
                self.update_progress()
            with self.reminder_lock:
                self.reminder_active = False

    def show_registration_screen(self):
        self.clear_window()
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True)
        title_label = ctk.CTkLabel(
            main_frame,
            text="Добро пожаловать!",
            font=("Arial", 24, "bold"),
            text_color="#4CAF50"
        )
        title_label.place(relx=0.5, rely=0.3, anchor="center")
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.place(relx=0.5, rely=0.5, anchor="center")
        register_button = ctk.CTkButton(
            buttons_frame,
            text="Зарегистрироваться",
            command=self.register,
            corner_radius=15,
            font=("Arial", 16, "bold"),
            width=200,
            height=40
        )
        register_button.pack(pady=15, fill="x")
        self.update_widget_styles(main_frame)

    def register(self):
        self.clear_window()
        self.register_frame = ctk.CTkFrame(self)
        self.register_frame.pack(fill="both", expand=True)
        ctk.CTkLabel(self, text="Регистрация", font=("Arial", 20, "bold")).pack(pady=12, padx=10)
        username_entry = ctk.CTkEntry(self, placeholder_text="Логин")
        username_entry.pack(pady=12, padx=10)
        password_entry = ctk.CTkEntry(self, placeholder_text="Пароль", show="*")
        password_entry.pack(pady=12, padx=10)
        gender_var = ctk.StringVar(value="male")
        gender_frame = ctk.CTkFrame(self, fg_color="transparent")
        gender_frame.pack(pady=10)
        ctk.CTkRadioButton(gender_frame, text="Мужской", variable=gender_var, value="male").pack(side="left", padx=10)
        ctk.CTkRadioButton(gender_frame, text="Женский", variable=gender_var, value="female").pack(side="left", padx=10)
        def complete_registration():
            username = username_entry.get()
            password = password_entry.get()
            gender = gender_var.get()
            if not username or not password:
                self.error_label.configure(text="Логин и пароль не могут быть пустыми")
                return
            if username in self.user_data:
                self.error_label.configure(text="Пользователь уже существует")
                return
            daily_goal = 3700 if gender == "male" else 2700
            self.user_data[username] = {
                "password": password,
                "daily_goal": daily_goal,
                "consumed": 0,
                "gender": gender
            }
            save_data(DATA_FILE, self.user_data)
            self.current_user = username
            self.settings["last_logged_in_user"] = username
            save_data(SETTINGS_FILE, self.settings)
            self.error_label.configure(text="Регистрация успешна!", text_color="green")
            self.show_main_content()
        register_button = ctk.CTkButton(
            self,
            text="Зарегистрироваться",
            command=complete_registration,
            corner_radius=15,
            font=("Arial", 16, "bold")
        )
        register_button.pack(pady=12, padx=10)
        self.error_label = ctk.CTkLabel(self, text="", text_color="red")
        self.error_label.pack(pady=10)

    def show_main_content(self):
        self.clear_window()
        if not self.current_user or self.current_user not in self.user_data:
            print("Ошибка: Текущий пользователь не найден.")
            return
        user_data = self.user_data[self.current_user]
        if "daily_goal" not in user_data or "consumed" not in user_data or "gender" not in user_data:
            print("Ошибка: Некорректные данные пользователя.")
            return
        ctk.CTkLabel(self, text=f"Привет, {self.current_user}!", font=("Arial", 24, "bold"), text_color="#4CAF50").pack(pady=20)
        self.progress_label = ctk.CTkLabel(self, text="Прогресс: 0%", font=("Arial", 18))
        self.progress_label.pack(pady=10)
        self.progress_bar = ctk.CTkProgressBar(self, width=400, height=20)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=10)
        self.goal_label = ctk.CTkLabel(self, text=f"Цель: {user_data['daily_goal']} мл", font=("Arial", 16))
        self.goal_label.pack(pady=10)
        gender = user_data["gender"]
        base_interval = self.settings.get("interval_male", 45*60) if gender == "male" else self.settings.get("interval_female", 60*60)
        daily_goal = user_data["daily_goal"]
        per_interval_ml = daily_goal / (24 * 60 * 60 / base_interval)
        interval_min = base_interval // 60
        self.interval_label = ctk.CTkLabel(self, 
            text=f"Базовый интервал: {interval_min} мин ({per_interval_ml:.1f} мл)", 
            font=("Arial", 14))
        self.interval_label.pack(pady=5)
        self.goal_entry = ctk.CTkEntry(self, placeholder_text="Новая цель (мл)")
        self.goal_entry.pack(pady=10)
        set_goal_button = ctk.CTkButton(
            self,
            text="Установить цель",
            command=lambda: self.set_goal(int(self.goal_entry.get())),
            corner_radius=15,
            font=("Arial", 16, "bold")
        )
        set_goal_button.pack(pady=10, ipadx=20, ipady=5)
        reset_goal_button = ctk.CTkButton(
            self,
            text="Сбросить цель",
            command=self.reset_goal,
            corner_radius=15,
            font=("Arial", 16, "bold")
        )
        reset_goal_button.pack(pady=10, ipadx=20, ipady=5)
        settings_button = ctk.CTkButton(
            self,
            text="Настройки",
            command=self.open_settings,
            corner_radius=15,
            font=("Arial", 16, "bold")
        )
        settings_button.pack(pady=10, ipadx=20, ipady=5)
        self.update_progress()

    def set_goal(self, new_goal):
        if new_goal > 0:
            self.user_data[self.current_user]["daily_goal"] = new_goal
            if self.current_user != "Гость":
                save_data(DATA_FILE, self.user_data)
            self.goal_label.configure(text=f"Цель: {new_goal} мл")
            self.update_progress()
            self.update_interval(new_goal)

    def update_interval(self, new_goal):
        gender = self.user_data[self.current_user]["gender"]
        base_interval = self.settings.get("interval_male", 45*60) if gender == "male" else self.settings.get("interval_female", 60*60)
        per_interval_ml = new_goal / (24 * 60 * 60 / base_interval)
        interval_min = base_interval // 60
        self.interval_label.configure(text=f"Базовый интервал: {interval_min} мин ({per_interval_ml:.1f} мл)")

    def reset_goal(self):
        self.user_data[self.current_user]["consumed"] = 0
        if self.current_user != "Гость":
            save_data(DATA_FILE, self.user_data)
        self.update_progress()

    def add_water(self, amount):
        if amount > 0:
            self.user_data[self.current_user]["consumed"] += amount
            if self.current_user != "Гость":
                save_data(DATA_FILE, self.user_data)
            self.update_progress()

    def update_progress(self):
        goal = self.user_data[self.current_user]["daily_goal"]
        consumed = self.user_data[self.current_user]["consumed"]
        progress = min(consumed / goal, 1) if goal > 0 else 0
        self.progress_bar.set(progress)
        self.progress_label.configure(text=f"Прогресс: {int(progress * 100)}%")
        if progress >= 1:
            self.show_completion_message()

    def show_completion_message(self):
        with self.reminder_lock:
            if self.check_progress_completed():
                return
        completion_frame = ctk.CTkFrame(self, fg_color="transparent")
        completion_frame.pack(pady=20, padx=20, fill="both", expand=True)
        theme = THEMES.get(self.settings.get("theme_color", "Базовый"), THEMES["Базовый"])
        ctk.CTkLabel(completion_frame, text="🎉 Поздравляем! 🎉", font=("Arial", 26, "bold"), text_color=theme["text"]).pack(pady=15)
        ctk.CTkLabel(
            completion_frame,
            text="Вы выполнили суточную норму!\nВозвращайтесь завтра.",
            font=("Arial", 18),
            text_color=theme["text"],
            justify="center"
        ).pack(pady=15)
        stats_frame = ctk.CTkFrame(completion_frame, fg_color=theme["secondary"])
        stats_frame.pack(pady=10, padx=10, fill="x")
        total_ml = self.user_data[self.current_user]["consumed"]
        daily_goal = self.user_data[self.current_user]["daily_goal"]
        percentage = (total_ml / daily_goal) * 100 if daily_goal > 0 else 100
        ctk.CTkLabel(stats_frame, text=f"Выпили: {total_ml} мл", font=("Arial", 16), text_color=theme["text"]).pack(anchor="w", padx=10, pady=5)
        ctk.CTkLabel(stats_frame, text=f"Цель: {daily_goal} мл", font=("Arial", 16), text_color=theme["text"]).pack(anchor="w", padx=10, pady=5)
        ctk.CTkLabel(stats_frame, text=f"Процент выполнения: {percentage:.2f}%", font=("Arial", 16), text_color=theme["text"]).pack(anchor="w", padx=10, pady=5)
        ok_button = ctk.CTkButton(
            completion_frame,
            text="OK",
            command=lambda: [completion_frame.destroy(), self.show_main_content()],
            corner_radius=15,
            font=("Arial", 16, "bold"),
            fg_color=theme["button_fg"],
            hover_color=theme["button_hover"]
        )
        ok_button.pack(pady=15, ipadx=20, ipady=5)
        with self.reminder_lock:
            self.reminder_active = False
        self.settings["reminder_interval_hours"] = 0
        self.settings["reminder_interval_minutes"] = 0
        self.settings["reminder_interval_seconds"] = 0
        save_data(SETTINGS_FILE, self.settings)

    def open_settings(self):
        self.clear_window()
        theme = THEMES.get(self.settings.get("theme_color", "Базовый"), THEMES["Базовый"])
        ctk.CTkLabel(self, text="Основные настройки", font=("Arial", 20, "bold"), text_color=theme["text"]).pack(pady=15)
        theme_var = ctk.StringVar(value=self.settings.get("theme_color", "Базовый"))
        theme_menu = ctk.CTkOptionMenu(
            self,
            variable=theme_var,
            values=list(THEMES.keys()),
            fg_color=theme["button_fg"],
            button_color=theme["button_hover"],
            button_hover_color=theme["button_fg"],
            font=("Arial", 14),
            dropdown_font=("Arial", 14)
        )
        theme_menu.pack(pady=5)
        transparency_var = ctk.DoubleVar(value=self.attributes("-alpha"))
        ctk.CTkLabel(self, text="Прозрачность интерфейса", font=("Arial", 16), text_color=theme["text"]).pack(pady=5)
        transparency_slider = ctk.CTkSlider(
            self,
            from_=0.5,
            to=1.0,
            variable=transparency_var,
            button_color=theme["secondary"],
            button_hover_color=theme["secondary"],
            progress_color=theme["secondary"]
        )
        transparency_slider.pack(pady=5)
        ctk.CTkLabel(self, text="Настройки уведомлений", font=("Arial", 20, "bold"), text_color=theme["text"]).pack(pady=15)
        sound_enabled_var = ctk.BooleanVar(value=self.settings.get("sound_enabled", True))
        sound_checkbox = ctk.CTkCheckBox(
            self,
            text="Включить звук",
            variable=sound_enabled_var,
            checkbox_height=20,
            checkbox_width=20,
            onvalue=True,
            offvalue=False,
            font=("Arial", 16),
            text_color=theme["text"]
        )
        sound_checkbox.pack(pady=5)
        selected_sound_var = ctk.StringVar(value=self.settings.get("selected_sound", "sound1"))
        ctk.CTkLabel(self, text="Выбор звука", font=("Arial", 16), text_color=theme["text"]).pack(pady=5)
        sound_menu = ctk.CTkOptionMenu(
            self,
            variable=selected_sound_var,
            values=list(self.sounds.keys()),
            fg_color=theme["button_fg"],
            button_color=theme["button_hover"],
            button_hover_color=theme["button_fg"],
            font=("Arial", 14),
            dropdown_font=("Arial", 14)
        )
        sound_menu.pack(pady=5)
        def preview_sound():
            selected_sound = selected_sound_var.get()
            sound_path = self.sounds.get(selected_sound)
            if sound_path and os.path.exists(sound_path):
                pygame.mixer.music.load(sound_path)
                pygame.mixer.music.play()
        preview_button = ctk.CTkButton(
            self,
            text="Прослушать звук",
            command=preview_sound,
            fg_color=theme["button_fg"],
            hover_color=theme["button_hover"],
            corner_radius=15,
            font=("Arial", 16, "bold")
        )
        preview_button.pack(pady=10, ipadx=20, ipady=5)
        ctk.CTkLabel(self, text="Интервал напоминаний", font=("Arial", 20, "bold"), text_color=theme["text"]).pack(pady=15)
        interval_hours = ctk.IntVar(value=self.settings.get("reminder_interval_hours", 1))
        interval_minutes = ctk.IntVar(value=self.settings.get("reminder_interval_minutes", 0))
        interval_seconds = ctk.IntVar(value=self.settings.get("reminder_interval_seconds", 0))
        ctk.CTkLabel(self, text="Интервал напоминаний (ЧЧ:ММ:СС)", font=("Arial", 16), text_color=theme["text"]).pack(pady=5)
        interval_frame = ctk.CTkFrame(self, fg_color="transparent")
        interval_frame.pack(pady=5)
        hours_spinbox = ctk.CTkOptionMenu(interval_frame, variable=interval_hours, values=[f"{i:02}" for i in range(24)], 
                                          width=60, height=30, fg_color=theme["button_fg"], button_color=theme["button_hover"], 
                                          button_hover_color=theme["button_fg"], font=("Arial", 14), dropdown_font=("Arial", 14))
        hours_spinbox.grid(row=0, column=0, padx=5)
        hours_spinbox.bind("<MouseWheel>", lambda e: self.spinbox_scroll(e, interval_hours, 24))
        minutes_spinbox = ctk.CTkOptionMenu(interval_frame, variable=interval_minutes, values=[f"{i:02}" for i in range(60)],
                                            width=60, height=30, fg_color=theme["button_fg"], button_color=theme["button_hover"], 
                                            button_hover_color=theme["button_fg"], font=("Arial", 14), dropdown_font=("Arial", 14))
        minutes_spinbox.grid(row=0, column=1, padx=5)
        minutes_spinbox.bind("<MouseWheel>", lambda e: self.spinbox_scroll(e, interval_minutes, 60))
        seconds_spinbox = ctk.CTkOptionMenu(interval_frame, variable=interval_seconds, values=[f"{i:02}" for i in range(60)],
                                            width=60, height=30, fg_color=theme["button_fg"], button_color=theme["button_hover"], 
                                            button_hover_color=theme["button_fg"], font=("Arial", 14), dropdown_font=("Arial", 14))
        seconds_spinbox.grid(row=0, column=2, padx=5)
        seconds_spinbox.bind("<MouseWheel>", lambda e: self.spinbox_scroll(e, interval_seconds, 60))
        def reset_all_settings():
            confirm = ctk.CTkInputDialog(
                text="Вы уверены, что хотите сбросить все настройки? Это действие нельзя отменить.",
                title="Подтверждение сброса"
            ).get_input()
            if confirm and confirm.lower() in ["да", "yes"]:
                default_settings = {
                    "appearance_mode": "Light",
                    "sound_enabled": True,
                    "selected_sound": "sound1.mp3",
                    "reminder_interval_hours": 1,
                    "reminder_interval_minutes": 0,
                    "reminder_interval_seconds": 0,
                    "last_logged_in_user": "Гость",
                    "theme_color": "Базовый",
                    "reset_time": "00:00",
                    "daily_base_male": 3700,
                    "daily_base_female": 2700,
                    "interval_male": 45 * 60,
                    "interval_female": 60 * 60
                }
                self.settings = default_settings
                save_data(SETTINGS_FILE, self.settings)
                self.apply_settings()
                self.show_main_content()
        reset_button = ctk.CTkButton(
            self,
            text="Сброс всех настроек",
            command=reset_all_settings,
            fg_color="#FF9800",
            hover_color="#F57C00",
            corner_radius=15,
            font=("Arial", 16, "bold")
        )
        reset_button.pack(pady=20, ipadx=20, ipady=5)
        def save_settings_with_restart_warning():
            try:
                self.settings["theme_color"] = theme_var.get()
                self.settings["sound_enabled"] = sound_enabled_var.get()
                self.settings["selected_sound"] = selected_sound_var.get()
                self.settings["reminder_interval_hours"] = interval_hours.get()
                self.settings["reminder_interval_minutes"] = interval_minutes.get()
                self.settings["reminder_interval_seconds"] = interval_seconds.get()
                self.settings["reset_time"] = reset_time_var.get()
                save_data(SETTINGS_FILE, self.settings)
                self.attributes("-alpha", transparency_var.get())
                self.apply_settings()
                from tkinter import messagebox
                messagebox.showwarning(
                    "Перезапуск рекомендуется",
                    "Для корректного применения настроек рекомендуется перезапустить приложение."
                )
                self.show_main_content()
            except Exception as e:
                print(f"Ошибка при сохранении настроек: {e}")
        save_button = ctk.CTkButton(
            self,
            text="Сохранить",
            command=save_settings_with_restart_warning,
            fg_color="#E91E63",
            hover_color="#C2185B",
            corner_radius=15,
            font=("Arial", 16, "bold")
        )
        save_button.pack(pady=20, ipadx=20, ipady=5)
        reset_time_var = ctk.StringVar(value=self.settings.get("reset_time", "00:00"))
        ctk.CTkLabel(
            self,
            text="Время сброса данных (ЧЧ:ММ)",
            font=("Arial", 16),
            text_color=theme["text"]
        ).pack(pady=5)
        reset_time_entry = ctk.CTkEntry(
            self,
            textvariable=reset_time_var,
            font=("Arial", 14)
        )
        reset_time_entry.pack(pady=5)
        logout_button = ctk.CTkButton(
            self,
            text="Выйти из аккаунта",
            command=self.logout,
            fg_color="#E91E63",
            hover_color="#C2185B",
            corner_radius=15,
            font=("Arial", 16, "bold")
        )
        logout_button.pack(pady=15, ipadx=20, ipady=5)
        self.update_widget_styles(self)

    def spinbox_scroll(self, event, var, max_value):
        current_value = var.get()
        if event.delta > 0:
            new_value = (current_value + 1) % max_value
        else:
            new_value = (current_value - 1) % max_value
        var.set(new_value)

    def clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()

    def logout(self):
        self.settings["last_logged_in_user"] = None 
        save_data(SETTINGS_FILE, self.settings)
        self.current_user = None
        self.show_registration_screen()

if __name__ == "__main__":
    os.makedirs(os.path.join("sound"), exist_ok=True)
    os.makedirs(os.path.join("icons"), exist_ok=True)
    create_default_files()
    app = WaterApp()
    app.mainloop()