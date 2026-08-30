import customtkinter as ctk
import configparser
from recorder import get_audio_devices

class SetupWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Initial Setup")
        self.geometry("400x200")
        self.resizable(False, False)

        self.label = ctk.CTkLabel(
            self,
            text="First launch detected. Select your audio device:",
            wraplength=350
        )
        self.label.pack(pady=(20, 10))

        self.devices = get_audio_devices()
        self.device_names = [device['name'] for device in self.devices]
        self.device_selection = ctk.StringVar()

        if self.device_names:
            self.device_selection.set(self.device_names[0])

        self.device_dropdown = ctk.CTkOptionMenu(
            self,
            values=self.device_names,
            variable=self.device_selection
        )
        self.device_dropdown.pack(pady=10)

        self.submit_button = ctk.CTkButton(
            self,
            text="Submit",
            command=self.on_submit
        )
        self.submit_button.pack(pady=10)

        self.after_ids = []

    def on_submit(self):
        for after_id in self.tk.call('after', 'info'):
            self.after_cancel(after_id)
        
        for after_id in self.after_ids:  
            self.after_cancel(after_id)
        
        config = configparser.ConfigParser()
        
        selected_device = self.device_selection.get()
        device_info = next((device for device in self.devices if device['name'] == selected_device), None)
        
        config['Settings'] = {
            'mode': 'False',
            'cuda': 'True',
            'model': 'small',
            'audio_device': selected_device,
            'sample_rate': str(device_info['defaultSampleRate']) if device_info else '44100'
        }
        
        config['GUI'] = {
            'width': '800',
            'height': '240',
            'bottom_offset': '50',
            'bg_color': '#2e2e2e',
            'text_color': 'white',
            'font_family': 'Verdana',
            'font_size': '16',
            'alpha': '0.9',
            'always_on_top': 'True',
            'update_interval_ms': '100',
            'intelligent_timeout_sec': '4.0',
            'auto_scroll': 'True',
            'hide_titlebar': 'False'
        }

        with open('config.ini', 'w') as configfile:
            config.write(configfile)
        
        self.quit()
        self.destroy()

def run_setup():
    setup_window = SetupWindow()
    setup_window.mainloop()

if __name__ == "__main__":
    run_setup()