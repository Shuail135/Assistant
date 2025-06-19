import tkinter as tk
from tkinter import ttk, filedialog, messagebox

SETTINGS_FILE = "settings.json"

# Default settings
default_settings = {
    "theme": "light",
    "volume": 1.0,
    "music_provider": 0,
    "quit_command": "Quit",
    "file_import_path": "tts_models/GLaDOS-146",
    "similarity_threshold": 0.6
}

music_provider_map = {
    0: "YouTube Music",
    1: "YouTube",
    2: "Spotify",
    3: "Tidal"
}
music_text_to_id = {v: k for k, v in music_provider_map.items()} # Convert music_provider to index


# Main GUI class
class SettingsApp:
    def __init__(self, root):
        from settings.settings_config import get_settings
        self.settings = get_settings()
        self.root = root
        self.root.title("Assistant Configuration")
        self.widgets = []

        self.build_main_gui()
        self.build_advanced_gui()
        self.apply_theme(self.settings["theme"])


    def build_advanced_gui(self):
        self.advanced_frame = tk.Frame(root)
        self.similarity_threshold_var = tk.DoubleVar(value=self.settings["similarity_threshold"])

        self.add_label("Similarity Threshold", parent=self.advanced_frame)
        self.similarity_entry = self.make_entry(self.advanced_frame, self.similarity_threshold_var)
        self.similarity_entry.pack(fill="x")
        self.similarity_entry_pack_info = {"fill": "x"}
        self.advanced_visible = False

    def add_label(self, text, parent=None):
        label = tk.Label(parent or root, text=text)
        label.pack(anchor="w")
        self.widgets.append(label)

    def make_entry(self, parent, variable):
        theme = self.theme_var.get()
        if theme == "dark":
            entry = tk.Entry(parent, textvariable=variable,
                             bg="#3a3a3a", fg="#ffffff", insertbackground="#ffffff",
                             relief="flat", highlightthickness=1,
                             highlightbackground="#444444", highlightcolor="#666666")
        else:
            entry = tk.Entry(parent, textvariable=variable)
        self.widgets.append(entry)
        return entry


    def toggle_advanced(self):
        if self.advanced_visible:
            self.advanced_frame.pack_forget()
            self.advanced_visible = False
        else:
            self.advanced_frame.pack(pady=10, fill="x")
            self.advanced_visible = True

    def browse_file(self):
        filepath = filedialog.askopenfilename()
        if filepath:
            self.file_path_var.set(filepath)

    def save_all(self):
        from settings.settings_config import save_settings  # Make sure to import

        self.settings["theme"] = self.theme_var.get()
        self.settings["volume"] = self.volume_ui_var.get() / 100
        self.settings["music_provider"] = music_text_to_id.get(self.music_provider_var.get(), 0)
        self.settings["quit_command"] = self.quit_command_var.get()
        self.settings["file_import_path"] = self.file_path_var.get()
        self.settings["similarity_threshold"] = self.similarity_threshold_var.get()

        save_settings(self.settings)
        messagebox.showinfo("Settings Saved", "Your settings have been saved.")

    def build_main_gui(self):
        # GUI variables bound to config data
        self.theme_var = tk.StringVar(value=self.settings["theme"])
        self.theme_var.trace_add("write", lambda *args: self.apply_theme(self.theme_var.get()))

        self.volume_var = tk.DoubleVar(value=self.settings["volume"])
        self.music_provider_var = tk.StringVar(value=music_provider_map[self.settings["music_provider"]])
        self.quit_command_var = tk.StringVar(value=self.settings["quit_command"])
        self.file_path_var = tk.StringVar(value=self.settings["file_import_path"])

        # Theme selector
        self.add_label("Theme")
        theme_box = ttk.Combobox(root, textvariable=self.theme_var, values=["light", "dark"])
        theme_box.pack(fill="x")
        self.widgets.append(theme_box)

        # Volume slider
        self.volume_ui_var = tk.IntVar(value=int(self.settings["volume"] * 100))
        self.add_label("Volume")
        volume_slider = tk.Scale(root, from_=0, to=100, orient="horizontal", variable=self.volume_ui_var)
        volume_slider.pack(fill="x")
        self.widgets.append(volume_slider)

        # Music provider dropdown
        self.add_label("Music Provider")
        music_box = ttk.Combobox(root, textvariable=self.music_provider_var, values=list(music_provider_map.values()))
        music_box.pack(fill="x")
        self.widgets.append(music_box)

        # TTS model file path entry with browse button
        self.add_label("TTS Model File Path")
        file_frame = tk.Frame(root)
        file_frame.pack(fill="x")
        self.file_entry = self.make_entry(file_frame, self.file_path_var)
        self.file_entry.pack(side="left", fill="x", expand=True)
        self.file_entry_pack_info = {"side": "left", "fill": "x", "expand": True}
        file_btn = ttk.Button(file_frame, text="Browse", command=self.browse_file)
        file_btn.pack(side="right")
        self.widgets.extend([file_frame, file_btn])

        # Quit Command
        self.quit_label = tk.Label(root, text="Quit Command")
        self.quit_label.pack(anchor="w")
        self.widgets.append(self.quit_label)
        self.quit_entry = self.make_entry(root, self.quit_command_var)
        self.quit_entry.pack(fill="x")
        self.quit_entry_pack_info = {"fill": "x"}

        # Advanced settings button
        self.adv_btn = ttk.Button(root, text="Advanced Developer Settings", command=self.toggle_advanced)
        self.adv_btn.pack(pady=(10, 0))
        self.widgets.append(self.adv_btn)

        # Save button
        self.save_btn = ttk.Button(root, text="Save Settings", command=self.save_all)
        self.save_btn.pack(pady=10)
        self.widgets.append(self.save_btn)

    def apply_theme(self, theme):
        bg = "#1e1e1e" if theme == "dark" else "#f0f0f0"
        fg = "#ffffff" if theme == "dark" else "#000000"
        btn_bg = "#3a3a3a" if theme == "dark" else "#e0e0e0"

        self.root.configure(bg=bg)
        self.advanced_frame.configure(bg=bg)

        style = ttk.Style()
        style.theme_use("default")

        style.configure("TCombobox", fieldbackground=btn_bg, background=btn_bg, foreground=fg)
        style.configure("TButton", background=btn_bg, foreground=fg)
        style.configure("TEntry", fieldbackground=btn_bg, foreground=fg, insertcolor=fg)

        for widget in self.widgets:
            try:
                widget.configure(bg=bg, fg=fg)
            except:
                pass

        for child in self.advanced_frame.winfo_children():
            try:
                child.configure(bg=bg, fg=fg)
            except:
                pass

        # Recreate styled entries and labels
        self.quit_label.destroy()
        self.quit_entry.destroy()
        self.quit_label = tk.Label(root, text="Quit Command")
        self.quit_entry = self.make_entry(root, self.quit_command_var)

        # Insert above the two buttons
        self.quit_label = tk.Label(root, text="Quit Command", bg=bg, fg=fg)
        self.quit_entry = self.make_entry(root, self.quit_command_var)

        self.quit_label.pack(before=self.adv_btn, anchor="w")
        self.quit_entry.pack(before=self.adv_btn, **self.quit_entry_pack_info)
        self.widgets.append(self.quit_label)

        self.file_entry.destroy()
        self.file_entry = self.make_entry(self.file_entry.master, self.file_path_var)
        self.file_entry.pack(**self.file_entry_pack_info)

        self.similarity_entry.destroy()
        self.similarity_entry = self.make_entry(self.advanced_frame, self.similarity_threshold_var)
        self.similarity_entry.pack(**self.similarity_entry_pack_info)

# Launch the app
root = tk.Tk()
app = SettingsApp(root)
root.mainloop()

def open_gui():
    root = tk.Tk()
    app = SettingsApp(root)
    root.mainloop()
