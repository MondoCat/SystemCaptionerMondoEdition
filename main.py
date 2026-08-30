import customtkinter as ctk
import subprocess
import sys
import os
import threading
import queue
import time
import configparser
import webbrowser
import platform
from PIL import Image

from console import ConsoleWindow, QueueWriter
from setupGUI import run_setup

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

CONFIG_FILE = "config.ini"

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        if self.tooltip_window or not self.text:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + 20
        self.tooltip_window = tw = ctk.CTkToplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = ctk.CTkLabel(tw, text=self.text, wraplength=150, bg_color="#2e2e2e", text_color="white")
        label.pack()

    def hide_tooltip(self, event=None):
        tw = self.tooltip_window
        self.tooltip_window = None
        if tw:
            tw.destroy()

def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

class GuiSettingsWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("GUI Settings")
        self.geometry("380x440")
        self.resizable(False, False)
        
        self.config = configparser.ConfigParser()
        self.config.read(CONFIG_FILE)

        self.frame = ctk.CTkScrollableFrame(self, width=340, height=360)
        self.frame.pack(pady=15, padx=15, fill="both", expand=True)

        self.entries = {}
        
        gui_defaults = {
            'width': ('Width (px)', '800'),
            'height': ('Height (px)', '240'),
            'bottom_offset': ('Bottom Offset (px)', '50'),
            'bg_color': ('Background Color', '#2e2e2e'),
            'text_color': ('Text Color', 'white'),
            'font_family': ('Font Family', 'Verdana'),
            'font_size': ('Font Size', '16'),
            'alpha': ('Opacity (0.1 - 1.0)', '0.9'),
            'intelligent_timeout_sec': ('Intelligent Timeout (s)', '4.0')
        }

        for key, (label_text, default_val) in gui_defaults.items():
            lbl = ctk.CTkLabel(self.frame, text=label_text, anchor="w")
            lbl.pack(fill="x", padx=5, pady=(5, 0))
            
            val = self.config.get('GUI', key, fallback=default_val)
            entry = ctk.CTkEntry(self.frame)
            entry.insert(0, val)
            entry.pack(fill="x", padx=5, pady=(0, 5))
            self.entries[key] = entry

        save_btn = ctk.CTkButton(self, text="Save Settings", fg_color="green", hover_color="dark green", command=self.save_gui_config)
        save_btn.pack(pady=(0, 15))

    def save_gui_config(self):
        fresh_config = configparser.ConfigParser()
        if os.path.exists(CONFIG_FILE):
            fresh_config.read(CONFIG_FILE)
            
        if 'GUI' not in fresh_config:
            fresh_config['GUI'] = {}
            
        for key, entry in self.entries.items():
            fresh_config['GUI'][key] = entry.get()
            
        with open(CONFIG_FILE, 'w') as configfile:
            fresh_config.write(configfile)
            
        self.destroy()

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("System Captioner - MondoCat Edition")
        self.geometry("480x540") 
        self.resizable(True, True)

        cat_icon_path = os.path.join(get_base_path(), "cat.ico")
        default_icon_path = os.path.join(get_base_path(), "icon.ico")
        
        if os.path.exists(cat_icon_path):
            self.iconbitmap(cat_icon_path)
        elif os.path.exists(default_icon_path):
            self.iconbitmap(default_icon_path)

        border_path = os.path.join(get_base_path(), "border.png")
        if os.path.exists(border_path):
            try:
                self.border_img_base = Image.open(border_path)
                self.border_ctk = ctk.CTkImage(light_image=self.border_img_base, dark_image=self.border_img_base, size=(480, 540))
                self.bg_label = ctk.CTkLabel(self, text="", image=self.border_ctk)
                self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
                
                self.resize_timer = None
                self.bind("<Configure>", self.on_window_configure)
            except Exception as e:
                print(f"Failed to load border.png: {e}", flush=True)

        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=15, pady=15)

        self.intelligent_mode = ctk.BooleanVar()
        self.gpu_enabled = ctk.BooleanVar()
        self.model_selection = ctk.StringVar()
        self.app_running = False
        self.process = None

        self.console_queue = queue.Queue()
        sys.stdout = QueueWriter(self.console_queue)
        sys.stderr = QueueWriter(self.console_queue)

        self.console_window = ConsoleWindow(self.console_queue, self)
        self.console_window.withdraw()

        self.config = configparser.ConfigParser()
        self.load_config()

        self.intelligent_mode.set(self.config.getboolean('Settings', 'mode', fallback=False))
        self.gpu_enabled.set(self.config.getboolean('Settings', 'cuda', fallback=True))
        self.model_selection.set(self.config.get('Settings', 'model', fallback='small'))
        
        self.auto_scroll = ctk.BooleanVar()
        self.auto_scroll.set(self.config.getboolean('GUI', 'auto_scroll', fallback=True))
        
        self.hide_titlebar = ctk.BooleanVar()
        self.hide_titlebar.set(self.config.getboolean('GUI', 'hide_titlebar', fallback=False))

        self.start_button = ctk.CTkButton(self.main_frame, text="Start", command=self.toggle_app, fg_color="green", hover_color="dark green")
        self.start_button.pack(pady=(15, 10))

        self.btn_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.btn_frame.pack(pady=(0, 15))

        self.console_button = ctk.CTkButton(self.btn_frame, text="Console", width=130, command=self.open_console, fg_color="blue", hover_color="dark blue")
        self.console_button.pack(side="left", padx=5)

        self.gui_settings_button = ctk.CTkButton(self.btn_frame, text="GUI Settings", width=130, command=self.open_gui_settings, fg_color="purple", hover_color="#5e0087")
        self.gui_settings_button.pack(side="left", padx=5)

        self.checkbox_frame = ctk.CTkFrame(self.main_frame)
        self.checkbox_frame.pack(pady=(0, 10))

        self.inner_checkbox_frame = ctk.CTkFrame(self.checkbox_frame)
        self.inner_checkbox_frame.pack()

        self.intelligent_checkbox = ctk.CTkCheckBox(self.inner_checkbox_frame, text="Intelligent mode", variable=self.intelligent_mode, command=self.save_config)
        self.intelligent_checkbox.grid(row=0, column=0, sticky="w", padx=(0, 10))

        self.gpu_checkbox = ctk.CTkCheckBox(self.inner_checkbox_frame, text="Run on GPU", variable=self.gpu_enabled, command=self.save_config)
        self.gpu_checkbox.grid(row=1, column=0, sticky="w", padx=(0, 10), pady=(5, 0))

        self.autoscroll_checkbox = ctk.CTkCheckBox(self.inner_checkbox_frame, text="Auto Scroll", variable=self.auto_scroll, command=self.save_config)
        self.autoscroll_checkbox.grid(row=2, column=0, sticky="w", padx=(0, 10), pady=(5, 0))

        self.hide_titlebar_checkbox = ctk.CTkCheckBox(self.inner_checkbox_frame, text="Hide Titlebar", variable=self.hide_titlebar, command=self.save_config)
        self.hide_titlebar_checkbox.grid(row=3, column=0, sticky="w", padx=(0, 10), pady=(5, 0))

        self.model_frame = ctk.CTkFrame(self.main_frame)
        self.model_frame.pack(pady=(0, 10))

        self.model_label = ctk.CTkLabel(self.model_frame, text="Model:")
        self.model_label.pack(side="left", padx=(0, 5))

        self.model_dropdown = ctk.CTkOptionMenu(self.model_frame, values=["tiny", "base", "small", "medium", "large"], variable=self.model_selection, command=self.save_config)
        self.model_dropdown.pack(side="left")

        self.device_frame = ctk.CTkFrame(self.main_frame)
        self.device_frame.pack(pady=(0, 5))

        self.device_label = ctk.CTkLabel(self.device_frame, text="Audio Device:")
        self.device_label.pack(side="left", padx=(0, 5))

        self.devices = self.get_audio_devices()
        self.device_names = [device['name'] for device in self.devices]
        self.device_selection = ctk.StringVar()

        saved_device = self.config.get('Settings', 'audio_device', fallback='')
        if saved_device in self.device_names:
            self.device_selection.set(saved_device)
        elif self.device_names:
            self.device_selection.set(self.device_names[0])

        self.device_dropdown = ctk.CTkOptionMenu(self.device_frame, values=self.device_names, variable=self.device_selection, command=self.on_device_change)
        self.device_dropdown.pack(side="left")

        self.drag_note_label = ctk.CTkLabel(
            self.main_frame,
            text="(Right click window after starting to move window)",
            text_color="gray",
            font=("", 11, "italic")
        )
        self.drag_note_label.pack(pady=(0, 10))

        self.feedback_label = ctk.CTkLabel(
            self.main_frame,
            text="OG Program by Evermoving",
            text_color="light blue",
            cursor="hand2",
            font=("", -13, "underline")
        )
        self.feedback_label.pack(side="bottom", pady=(0, 5))
        self.feedback_label.bind("<Button-1>", lambda e: self.open_feedback_link())

        cat_path = os.path.join(get_base_path(), "cat.png")
        if os.path.exists(cat_path):
            try:
                cat_img = Image.open(cat_path)
                
                width, height = cat_img.size
                max_width = 370
                max_height = 140 
                
                ratio = min(max_width / width, max_height / height)
                new_width = int(width * ratio)
                new_height = int(height * ratio)
                
                self.cat_ctk = ctk.CTkImage(light_image=cat_img, dark_image=cat_img, size=(new_width, new_height))
                self.cat_label = ctk.CTkLabel(self.main_frame, text="", image=self.cat_ctk)
                self.cat_label.pack(side="bottom", expand=True, pady=(5, 5))
            except Exception as e:
                print(f"Failed to load cat.png: {e}", flush=True)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.TRANSCRIPTION_TIMEOUT = 20 
        self.last_transcription_start = 0
        self.current_transcription_file = None
        self.timeout_thread = None
        self.stop_timeout = threading.Event()

    def on_window_configure(self, event):
        if event.widget == self:
            if self.resize_timer:
                self.after_cancel(self.resize_timer)
            self.resize_timer = self.after(50, self.perform_bg_resize)

    def perform_bg_resize(self):
        new_w = self.winfo_width()
        new_h = self.winfo_height()
        if hasattr(self, 'border_ctk'):
            self.border_ctk.configure(size=(max(10, new_w), max(10, new_h)))

    def load_config(self):
        if not os.path.exists(CONFIG_FILE):
            run_setup()
        self.config.read(CONFIG_FILE)

    def save_config(self, *args):
        fresh_config = configparser.ConfigParser()
        if os.path.exists(CONFIG_FILE):
            fresh_config.read(CONFIG_FILE)
        
        if 'Settings' not in fresh_config:
            fresh_config['Settings'] = {}
            
        fresh_config['Settings']['mode'] = str(self.intelligent_mode.get())
        fresh_config['Settings']['cuda'] = str(self.gpu_enabled.get())
        fresh_config['Settings']['model'] = self.model_selection.get()
        fresh_config['Settings']['audio_device'] = self.device_selection.get()

        selected_device = self.device_selection.get()
        device_info = next((device for device in self.devices if device['name'] == selected_device), None)
        if device_info:
            fresh_config['Settings']['sample_rate'] = str(device_info['defaultSampleRate'])
            
        if 'GUI' not in fresh_config:
            fresh_config['GUI'] = {}
        fresh_config['GUI']['auto_scroll'] = str(self.auto_scroll.get())
        fresh_config['GUI']['hide_titlebar'] = str(self.hide_titlebar.get())

        with open(CONFIG_FILE, 'w') as configfile:
            fresh_config.write(configfile)
            
        self.config = fresh_config

    def open_gui_settings(self):
        GuiSettingsWindow(self)

    def toggle_app(self):
        if not self.app_running:
            self.start_app()
            self.start_button.configure(text="Stop", fg_color="red", hover_color="dark red")
        else:
            self.stop_app()
            self.start_button.configure(text="Start", fg_color="green", hover_color="dark green")

    def start_app(self):
        self.last_transcription_start = 0
        self.current_transcription_file = None
        
        base_dir = get_base_path()
        recordings_path = os.path.join(base_dir, "recordings")
        transcriptions_path = os.path.join(base_dir, "transcriptions.txt")

        if os.path.exists(recordings_path):
            try:
                for filename in os.listdir(recordings_path):
                    file_path = os.path.join(recordings_path, filename)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
            except Exception:
                pass
        else:
            os.makedirs(recordings_path)

        try:
            with open(transcriptions_path, 'w') as f:
                pass
        except Exception:
            pass

        self.start_button.configure(text="Stop", fg_color="red", hover_color="dark red")
        intelligent = self.intelligent_mode.get()
        cuda = self.gpu_enabled.get()
        model = self.model_selection.get()
        
        if getattr(sys, 'frozen', False):
            controller_executable = os.path.join(base_dir, 'Controller', 'Controller.exe')
            args = [controller_executable]
        else:
            controller_executable = os.path.join(base_dir, 'controller.py')
            args = [sys.executable, controller_executable]
        
        if intelligent:
            args.append("--intelligent")
        if cuda:
            args.append("--cuda")
        args.extend(["--model", model])
        
        selected_device = self.device_selection.get()
        device_index = next((device['index'] for device in self.devices if device['name'] == selected_device), None)
        if device_index is not None:
            args.extend(["--device-index", str(device_index)])
        
        self.process = subprocess.Popen(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        self.app_running = True

        self.stop_timeout.clear()
        self.timeout_thread = threading.Thread(target=self.monitor_timeout, daemon=True)
        self.timeout_thread.start()

        threading.Thread(target=self.read_process_output, daemon=True).start()
        threading.Thread(target=self.watch_console_queue, daemon=True).start()

    def stop_app(self):
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                try:
                    self.process.kill()
                except Exception:
                    pass
            except Exception:
                pass
            self.process = None

        if platform.system() == "Windows":
            try:
                subprocess.run(
                    ["taskkill", "/F", "/T", "/IM", "Controller.exe"], 
                    capture_output=True, 
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            except Exception:
                pass
            
        self.start_button.configure(text="Start", fg_color="green", hover_color="dark green")
        self.app_running = False
        self.stop_timeout.set()
        if self.timeout_thread and threading.current_thread() != self.timeout_thread:
            self.timeout_thread.join()
            self.timeout_thread = None

    def trigger_safe_restart(self):
        if self.app_running:
            self.stop_app()
            self.after(1000, self.start_app)

    def monitor_timeout(self):
        while self.app_running and not self.stop_timeout.is_set():
            if self.last_transcription_start > 0:
                elapsed_time = time.time() - self.last_transcription_start
                if elapsed_time > self.TRANSCRIPTION_TIMEOUT:
                    self.after(0, self.trigger_safe_restart)
                    break
            time.sleep(1)

    def read_process_output(self):
        if self.process and self.process.stdout:
            for line in iter(self.process.stdout.readline, ''):
                if not line:
                    break
                line = line.strip()
                
                if "SIGNAL_GUI_CLOSED" in line:
                    self.after(0, self.stop_app)
                    continue

                if "Starting transcription for" in line:
                    self.last_transcription_start = time.time()
                    self.current_transcription_file = line.split("...")[-2].split("recordings\\")[-1]
                if "Transcription completed" in line or "Error during transcription" in line:
                    self.last_transcription_start = 0
                    self.current_transcription_file = None

                if "ERROR" in line:
                    self.console_queue.put(f"controller.py ERROR: {line}")
                else:
                    self.console_queue.put(f"controller.py: {line}")
                    
            if self.app_running:
                self.after(0, self.stop_app)

    def open_console(self):
        if not self.console_window or not self.console_window.winfo_exists():
            self.console_window = ConsoleWindow(self.console_queue, self)
        else:
            self.console_window.deiconify()
            self.console_window.focus()

    def watch_console_queue(self):
        while self.app_running:
            time.sleep(1)

    def run(self):
        self.mainloop()

    def get_audio_devices(self):
        from recorder import get_audio_devices
        return get_audio_devices()

    def on_device_change(self, selected_device_name):
        device_info = next((device for device in self.devices if device['name'] == selected_device_name), None)
        if device_info:
            self.config['Settings']['sample_rate'] = str(device_info['defaultSampleRate'])
            self.config['Settings']['audio_device'] = selected_device_name
            with open(CONFIG_FILE, 'w') as configfile:
                self.config.write(configfile)

    def on_closing(self):
        if self.app_running:
            self.stop_app()
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                try:
                    self.process.kill()
                except Exception:
                    pass
            except Exception:
                pass
            self.process = None

        if platform.system() == "Windows":
            try:
                subprocess.run(
                    ["taskkill", "/F", "/T", "/IM", "Controller.exe"], 
                    capture_output=True, 
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            except Exception:
                pass
        # ----------------------------------

        if self.console_window and self.console_window.winfo_exists():
            self.console_window.destroy()
        self.quit()
        self.destroy()

    def open_feedback_link(self):
        webbrowser.open("https://github.com/evermoving/SystemCaptioner/issues")

if __name__ == "__main__":
    app = App()
    app.run()