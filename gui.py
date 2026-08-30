import tkinter as tk
from tkinter import scrolledtext
import queue
import time
import configparser
import os
import sys

def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

class SubtitleGUI:
    def __init__(self, update_queue, intelligent_mode=False):
        self.update_queue = update_queue
        self.intelligent_mode = intelligent_mode
        self.last_activity_time = time.time()
        self.should_show = False

        self.config = configparser.ConfigParser()
        self.config.read('config.ini')

        def safe_get(section, key, fallback, get_type=str):
            try:
                if get_type == int:
                    return self.config.getint(section, key, fallback=fallback)
                elif get_type == float:
                    return self.config.getfloat(section, key, fallback=fallback)
                elif get_type == bool:
                    return self.config.getboolean(section, key, fallback=fallback)
                else:
                    return self.config.get(section, key, fallback=fallback)
            except Exception:
                return fallback

        self.window_width = safe_get('GUI', 'width', 800, int)
        self.window_height = safe_get('GUI', 'height', 240, int)
        self.bottom_offset = safe_get('GUI', 'bottom_offset', 50, int)

        self.bg_color = safe_get('GUI', 'bg_color', '#2e2e2e')
        self.text_color = safe_get('GUI', 'text_color', 'white')
        self.font_family = safe_get('GUI', 'font_family', 'Verdana')
        self.font_size = safe_get('GUI', 'font_size', 16, int)
        self.window_alpha = safe_get('GUI', 'alpha', 0.9, float)
        self.always_on_top = safe_get('GUI', 'always_on_top', True, bool)

        self.update_interval = safe_get('GUI', 'update_interval_ms', 100, int)
        self.intelligent_timeout = safe_get('GUI', 'intelligent_timeout_sec', 4.0, float)
        self.auto_scroll = safe_get('GUI', 'auto_scroll', True, bool)
        self.hide_titlebar = safe_get('GUI', 'hide_titlebar', False, bool)

        self.current_width = self.window_width
        self.current_height = self.window_height
        self.current_hide_titlebar = self.hide_titlebar

        self.root = tk.Tk()
        self.root.title("System Captioner - MondoCat Edition")
        
        base_path = get_base_path()
        cat_icon_path = os.path.join(base_path, "cat.ico")
        default_icon_path = os.path.join(base_path, "icon.ico")
        
        if os.path.exists(cat_icon_path):
            self.root.iconbitmap(cat_icon_path)
        elif os.path.exists(default_icon_path):
            self.root.iconbitmap(default_icon_path)
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x_position = (screen_width // 2) - (self.window_width // 2)
        y_position = screen_height - self.window_height - self.bottom_offset
        self.root.geometry(f"{self.window_width}x{self.window_height}+{x_position}+{y_position}")
        
        try:
            self.root.attributes("-alpha", self.window_alpha)
            self.root.attributes("-topmost", self.always_on_top)
            self.root.configure(bg=self.bg_color)
        except Exception as e:
            print(f"Error applying window attributes: {e}", flush=True)
        
        self.text_area = scrolledtext.ScrolledText(
            self.root,
            wrap=tk.WORD,
            bg=self.bg_color,
            fg=self.text_color,
            font=(self.font_family, self.font_size),
            borderwidth=0,
            highlightthickness=0
        )
        self.text_area.pack(expand=True, fill='both')
        
        self.text_area.bind("<Key>", self.read_only_handler)

        self.text_area.bind("<ButtonPress-3>", self.start_move)
        self.text_area.bind("<ButtonRelease-3>", self.stop_move)
        self.text_area.bind("<B3-Motion>", self.do_move)
        self.root.bind("<ButtonPress-3>", self.start_move)
        self.root.bind("<ButtonRelease-3>", self.stop_move)
        self.root.bind("<B3-Motion>", self.do_move)

        self.start_x = 0
        self.start_y = 0
        self.win_x = 0
        self.win_y = 0

        self.root.after(50, lambda: self.root.overrideredirect(self.hide_titlebar))

        if self.intelligent_mode:
            self.root.withdraw()

        self.root.after(self.update_interval, self.update_subtitles)
        self.root.after(1000, self.poll_config_live) 

    def read_only_handler(self, event):
        if event.state & 0x0004 and event.keysym.lower() in ['c', 'a']:
            return None
        if event.keysym in ['Up', 'Down', 'Left', 'Right', 'Prior', 'Next', 'Home', 'End']:
            return None
        return "break"

    def safe_get(self, section, key, fallback, get_type=str):
        try:
            if get_type == int:
                return self.config.getint(section, key, fallback=fallback)
            elif get_type == float:
                return self.config.getfloat(section, key, fallback=fallback)
            elif get_type == bool:
                return self.config.getboolean(section, key, fallback=fallback)
            else:
                return self.config.get(section, key, fallback=fallback)
        except Exception:
            return fallback

    def start_move(self, event):
        self.start_x = event.x_root
        self.start_y = event.y_root
        self.win_x = self.root.winfo_x()
        self.win_y = self.root.winfo_y()

    def stop_move(self, event):
        pass

    def do_move(self, event):
        dx = event.x_root - self.start_x
        dy = event.y_root - self.start_y
        self.root.geometry(f"+{self.win_x + dx}+{self.win_y + dy}")

    def poll_config_live(self):
        try:
            if os.path.exists('config.ini'):
                temp_config = configparser.ConfigParser()
                temp_config.read('config.ini')
                
                bg = temp_config.get('GUI', 'bg_color', fallback=self.bg_color)
                fg = temp_config.get('GUI', 'text_color', fallback=self.text_color)
                font_fam = temp_config.get('GUI', 'font_family', fallback=self.font_family)
                font_sz = temp_config.getint('GUI', 'font_size', fallback=self.font_size)
                alpha = temp_config.getfloat('GUI', 'alpha', fallback=self.window_alpha)
                topmost = temp_config.getboolean('GUI', 'always_on_top', fallback=self.always_on_top)
                
                old_auto_scroll = self.auto_scroll
                self.auto_scroll = temp_config.getboolean('GUI', 'auto_scroll', fallback=self.auto_scroll)
                if self.auto_scroll and not old_auto_scroll:
                    self.text_area.yview(tk.END)
                
                self.intelligent_timeout = temp_config.getfloat('GUI', 'intelligent_timeout_sec', fallback=self.intelligent_timeout)
                
                new_width = temp_config.getint('GUI', 'width', fallback=self.current_width)
                new_height = temp_config.getint('GUI', 'height', fallback=self.current_height)
                new_hide = temp_config.getboolean('GUI', 'hide_titlebar', fallback=self.current_hide_titlebar)

                try:
                    self.root.configure(bg=bg)
                    self.text_area.configure(bg=bg, fg=fg, font=(font_fam, font_sz))
                    self.root.attributes("-alpha", alpha)
                    self.root.attributes("-topmost", topmost)
                    
                    if new_hide != self.current_hide_titlebar:
                        self.root.withdraw()
                        self.root.update_idletasks()
                        self.root.overrideredirect(new_hide)
                        self.root.update_idletasks()
                        if not self.intelligent_mode or self.should_show:
                            self.root.deiconify()
                        self.current_hide_titlebar = new_hide
                    
                    if new_width != self.current_width or new_height != self.current_height:
                        current_x = self.root.winfo_x()
                        current_y = self.root.winfo_y()
                        self.root.geometry(f"{new_width}x{new_height}+{current_x}+{current_y}")
                        self.current_width = new_width
                        self.current_height = new_height
                        self.text_area.yview(tk.END)

                except Exception as gui_err:
                    print(f"Error applying live config: {gui_err}", flush=True)
        except Exception as e:
            print(f"Error reading live config: {e}", flush=True)
        
        self.root.after(1000, self.poll_config_live)

    def update_subtitles(self):
        try:
            while True:
                transcription = self.update_queue.get_nowait()
                self.display_transcription(transcription)
                if self.intelligent_mode:
                    self.last_activity_time = time.time()
                    if not self.should_show:
                        self.root.deiconify()
                        self.should_show = True
        except queue.Empty:
            pass

        if self.intelligent_mode:
            if self.should_show and (time.time() - self.last_activity_time > self.intelligent_timeout):
                self.root.withdraw()
                self.should_show = False

        self.root.after(self.update_interval, self.update_subtitles)

    def display_transcription(self, transcription):
        self.text_area.insert(tk.END, transcription + "\n")
        
        if self.auto_scroll:
            self.text_area.yview(tk.END)

    def on_closing(self):
        self.root.withdraw()
        print("SIGNAL_GUI_CLOSED", flush=True)

    def run(self):
        self.root.mainloop()