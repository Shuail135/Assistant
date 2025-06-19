from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.slider import MDSlider
from kivymd.uix.textfield import MDTextField
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.tab import MDTabsBase
from kivymd.uix.tab import MDTabs
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.uix.widget import Widget

Window.size = (350, 600)

from settings.settings_config import get_settings, save_settings

music_provider_map = {
    0: "YouTube Music",
    1: "YouTube",
    2: "Spotify",
    3: "Tidal"
}
music_text_to_id = {v: k for k, v in music_provider_map.items()}


class GeneralTab(MDBoxLayout, MDTabsBase):
    def __init__(self, screen, **kwargs):
        super().__init__(orientation='vertical', spacing=dp(20), padding=dp(20), **kwargs)
        self.screen = screen
        self.build()

    def build(self):
        self.add_widget(MDLabel(text="Theme", font_style="Subtitle1"))
        self.add_widget(self.screen.theme_text)

        self.add_widget(MDLabel(text="Volume", font_style="Subtitle1"))
        self.add_widget(self.screen.volume_slider)

        self.add_widget(MDLabel(text="Music Provider", font_style="Subtitle1"))
        self.add_widget(self.screen.music_provider_field)

        self.add_widget(MDLabel(text="Quit Command", font_style="Subtitle1"))
        self.add_widget(self.screen.quit_command)

        self.add_widget(MDLabel(text="TTS Model File Path", font_style="Subtitle1"))
        self.add_widget(self.screen.file_path)


class AdvancedTab(MDBoxLayout, MDTabsBase):
    def __init__(self, screen, **kwargs):
        super().__init__(orientation='vertical', spacing=dp(20), padding=dp(20), **kwargs)
        self.screen = screen
        self.build()

    def build(self):
        self.add_widget(MDLabel(text="Similarity Threshold", font_style="Subtitle1"))
        self.add_widget(self.screen.similarity_input)



class SettingsScreen(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", **kwargs)
        self.settings = get_settings()

        self.file_manager = MDFileManager(
            exit_manager=self.exit_file_manager,
            select_path=self.select_file_path,
        )

        self.app = MDApp.get_running_app()

        # Theme
        self.theme_spinner = MDDropdownMenu(
            caller=None,
            items=[{"text": t, "on_release": lambda x=t: self.change_theme(x)} for t in ["light", "dark"]],
            width_mult=3
        )
        self.theme_text = MDTextField(text=self.settings["theme"], readonly=True)
        self.theme_text.bind(on_touch_down=self.open_theme_menu)

        # Volume
        self.volume_slider = MDSlider(
            min=0, max=100, value=self.settings["volume"]*100, step=1,
            size_hint_y=None, height=dp(40)
        )

        # Music Provider
        self.music_provider_field = MDTextField(
            text=music_provider_map[self.settings["music_provider"]],
            hint_text="Select Music Provider", readonly=True
        )
        self.music_provider_field.bind(on_touch_down=self.open_music_menu)
        menu_items = [
            {"text": name, "viewclass": "OneLineListItem", "on_release": lambda x=name: self.set_music_provider(x)}
            for name in music_provider_map.values()
        ]
        self.music_menu = MDDropdownMenu(
            caller=self.music_provider_field,
            items=menu_items,
            width_mult=4
        )

        # Quit Command
        self.quit_command = MDTextField(text=self.settings["quit_command"])

        # File Path
        self.file_path = MDTextField(
            text=self.settings["file_import_path"], hint_text="Choose file", readonly=True
        )
        self.file_path.bind(on_touch_down=self.open_file_picker)

        # Advanced Setting Field
        self.similarity_input = MDTextField(text=str(self.settings["similarity_threshold"]))

        # Tabs
        self.tabs = MDTabs()
        self.tabs.add_widget(GeneralTab(self, title="General"))
        self.tabs.add_widget(AdvancedTab(self, title="Advanced"))
        self.add_widget(self.tabs)

        bottom_spacer = Widget(size_hint_y=None, height=dp(10))

        # Save Button
        self.save_button = MDRaisedButton(
            text="Save Settings",
            on_release=self.save_all,
            pos_hint={"center_x": 0.5}
        )

        self.add_widget(self.save_button)
        self.add_widget(bottom_spacer)
    def open_theme_menu(self, instance, touch):
        if instance.collide_point(*touch.pos):
            self.theme_spinner.caller = instance
            self.theme_spinner.open()

    def open_music_menu(self, instance, touch):
        if instance.collide_point(*touch.pos):
            self.music_menu.caller = instance
            self.music_menu.open()

    def change_theme(self, theme):
        self.theme_text.text = theme
        self.app.theme_cls.theme_style = theme.capitalize()

    def set_music_provider(self, name):
        self.music_provider_field.text = name
        self.music_menu.dismiss()

    def open_file_picker(self, instance, touch):
        if instance.collide_point(*touch.pos):
            self.file_manager.show("/")

    def select_file_path(self, path):
        self.file_path.text = path
        self.exit_file_manager()

    def exit_file_manager(self, *args):
        self.file_manager.close()

    def save_all(self, _instance):
        self.settings["theme"] = self.theme_text.text
        self.settings["volume"] = self.volume_slider.value / 100
        self.settings["music_provider"] = music_text_to_id.get(self.music_provider_field.text, 0)
        self.settings["quit_command"] = self.quit_command.text
        self.settings["file_import_path"] = self.file_path.text
        try:
            self.settings["similarity_threshold"] = float(self.similarity_input.text)
        except ValueError:
            self.settings["similarity_threshold"] = 0.6
        save_settings(self.settings)


class SettingsApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = get_settings().get("theme", "Light").capitalize()
        return SettingsScreen()


def open_gui():
    SettingsApp().run()

if __name__ == "__main__":
    open_gui()