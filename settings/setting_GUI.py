import platform
import os

from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.slider import MDSlider
from kivymd.uix.textfield import MDTextField
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.tab import MDTabsBase, MDTabs
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.uix.carousel import Carousel
from settings.settings_config import get_settings, save_settings
from kivy.effects.scroll import ScrollEffect
from kivy.clock import Clock
from kivymd.toast import toast
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.utils import get_color_from_hex

Window.size = (350, 600)

music_provider_map = {
    0: "YouTube Music",
    1: "YouTube",
    2: "Spotify",
    3: "Tidal"
}
music_text_to_id = {v: k for k, v in music_provider_map.items()}

sampling_rates = [16000, 22050, 24000, 44100]

hifigan_versions = ["v1", "v1b"]

# Mouse scrolling
class MouseOnlyScrollView(ScrollView):
    def __init__(self, **kwargs):
        kwargs.setdefault('effect_cls', ScrollEffect)
        super().__init__(**kwargs)
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if touch.is_mouse_scrolling:
                return super().on_touch_down(touch)
            return super().on_touch_down(touch)
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        return False  if self.collide_point(*touch.pos) else super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            if touch.is_mouse_scrolling:
                return super().on_touch_up(touch)
            return super().on_touch_up(touch)
        return super().on_touch_up(touch)

class CustomInputRow(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="horizontal", spacing=dp(10), size_hint_y=None, height=dp(50), **kwargs)

        # Text field that expands
        self.input_field = MDTextField(
            hint_text="Manual open settings only",
            size_hint_x=1,
            height=dp(50)
        )

        # Fixed-size button
        self.action_button = MDRaisedButton(
            text="Test",
            size_hint_x=None,
            width=dp(80),
            on_release=self.on_button_pressed
        )

        self.add_widget(self.input_field)
        self.add_widget(self.action_button)

    def on_button_pressed(self, instance):
        Clock.schedule_once(lambda dt: self.run_speak(), 0.1)

    def run_speak(self):
        string = self.input_field.text
        if string != "":
            from tts_controller import speak
            speak(string, True)

class GeneralTab(MouseOnlyScrollView, MDTabsBase):
    def __init__(self, screen, **kwargs):
        super().__init__(**kwargs)
        self.screen = screen

        self.container = MDBoxLayout(
            orientation='vertical',
            spacing=dp(0),
            padding=dp(15),
            size_hint_y=None
        )
        self.container.bind(minimum_height=self.container.setter('height'))

        self.build()
        self.add_widget(self.container)


    def build(self):
        def make_label(text, height=dp(0)):
            return MDLabel(
                text=text,
                font_style="Subtitle1",
                size_hint_y=None,
                height=height
            )

        def fix_widget(widget, height=dp(50)):
            widget.size_hint_y = None
            widget.height = height
            return widget

        def white_space(height=dp(20)):
            self.container.add_widget(Widget(size_hint_y=None, height=height))

        white_space()

        self.container.add_widget(make_label("Theme"))
        self.container.add_widget(fix_widget(self.screen.theme_text, height=dp(63)))

        white_space()

        self.container.add_widget(make_label("Volume"))
        self.container.add_widget(fix_widget(self.screen.volume_slider, dp(40)))

        white_space()

        self.container.add_widget(make_label("Music Provider"))
        self.container.add_widget(fix_widget(self.screen.music_provider_field))

        white_space()

        self.container.add_widget(make_label("Quit Command"))
        self.container.add_widget(fix_widget(self.screen.quit_command, height=dp(63)))



class TTSTab(MouseOnlyScrollView, MDTabsBase):
    def __init__(self, screen, **kwargs):
        super().__init__(**kwargs)
        self.screen = screen

        self.container = MDBoxLayout(
            orientation='vertical',
            spacing=dp(0),
            padding=dp(15),
            size_hint_y=None
        )
        self.container.bind(minimum_height=self.container.setter('height'))

        self.build()
        self.add_widget(self.container)


    def build(self):
        def make_label(text, height=dp(0)):
            return MDLabel(
                text=text,
                font_style="Subtitle1",
                size_hint_y=None,
                height=height
            )

        def fix_widget(widget, height=dp(50)):
            widget.size_hint_y = None
            widget.height = height
            return widget

        def white_space(height=dp(20)):
            self.container.add_widget(Widget(size_hint_y=None, height=height))

        white_space()

        self.container.add_widget(make_label("TTS Model File Path"))
        self.container.add_widget(fix_widget(self.screen.file_path))

        white_space()

        self.container.add_widget(make_label("Max Decoder Steps"))
        self.container.add_widget(fix_widget(self.screen.decoder_steps_input, height=dp(63)))

        white_space()

        self.container.add_widget(make_label("Sampling Rate"))
        self.container.add_widget(fix_widget(self.screen.sampling_rate_field, height=dp(63)))

        white_space()

        self.container.add_widget(make_label("Stop Threshold"))
        self.container.add_widget(fix_widget(self.screen.stop_threshold, height=dp(63)))

        white_space()

        self.container.add_widget(make_label("Hifigan Config"))
        self.container.add_widget(fix_widget(self.screen.hifigan_version_field, height=dp(63)))

        white_space()

        self.container.add_widget(make_label("Hifigan Path"))
        self.container.add_widget(fix_widget(self.screen.hifigan_file_path))

        white_space()

        self.container.add_widget(make_label("Max duration of Speech"))
        self.container.add_widget(fix_widget(self.screen.max_duration, height=dp(63)))

        white_space()

        self.container.add_widget(make_label("Superres Strength"))
        self.container.add_widget(fix_widget(self.screen.superres_strength, height=dp(63)))

        white_space()

        self.container.add_widget(make_label("Use Pronunciation"))
        self.container.add_widget(fix_widget(self.screen.use_pronunciation, height=dp(63)))

        white_space()

        self.container.add_widget(make_label("Denoiser Strength"))
        self.container.add_widget(fix_widget(self.screen.denoiser_strength, height=dp(63)))

        white_space()

        row = CustomInputRow()
        self.container.add_widget(row)


class AdvancedTab(MouseOnlyScrollView, MDTabsBase):
    def __init__(self, screen, **kwargs):
        super().__init__(**kwargs)
        self.screen = screen

        self.container = MDBoxLayout(
            orientation='vertical',
            spacing=dp(0),
            padding=dp(15),
            size_hint_y=None
        )
        self.container.bind(minimum_height=self.container.setter('height'))

        self.build()
        self.add_widget(self.container)

    def build(self):
        def make_label(text, height=dp(0)):
            return MDLabel(
                text=text,
                font_style="Subtitle1",
                size_hint_y=None,
                height=height
            )

        def fix_widget(widget, height=dp(50)):
            widget.size_hint_y = None
            widget.height = height
            return widget

        def white_space(height=dp(20)):
            self.container.add_widget(Widget(size_hint_y=None, height=height))

        white_space()

        self.container.add_widget(make_label("Similarity Threshold"))
        self.container.add_widget(fix_widget(self.screen.similarity_input, height=dp(63)))


class NoSwipeTabs(MDTabs):
    def on_kv_post(self, base_widget):
        super().on_kv_post(base_widget)
        if isinstance(self.ids.carousel, Carousel):
            self.ids.carousel.scroll_timeout = 0


class SettingsScreen(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", **kwargs)
        self.settings = get_settings()
        self.app = MDApp.get_running_app()

        if MDApp.get_running_app().theme_cls.theme_style == "Dark":
            self.md_bg_color = get_color_from_hex("#2A2A2A")

        self.file_manager = MDFileManager(
            exit_manager=self.exit_file_manager,
            select_path=self.select_file_path,
        )

        # --- Theme Dropdown ---
        self.theme_text = MDTextField(
            text=self.settings["theme"],
            hint_text="Select Theme",
            readonly=True,
            size_hint_y=None,
            height=dp(50)
        )
        self.theme_text.bind(on_touch_down=self.open_theme_menu)

        # --- Volume Slider ---
        self.volume_slider = MDSlider(
            min=0, max=100, value=self.settings["volume"] * 100, step=1,
            size_hint_y=None, height=dp(40)
        )

        # --- Music Provider Dropdown ---
        self.music_provider_field = MDTextField(
            text=music_provider_map[self.settings["music_provider"]],
            hint_text="Select Music Provider",
            readonly=True,
            size_hint_y=None,
            height=dp(50)
        )
        self.music_provider_field.bind(on_touch_down=self.open_music_menu)

        # --- Quit Command ---
        self.quit_command = MDTextField(
            text=self.settings["quit_command"],
            hint_text="Type Quit Command here",
            size_hint_y=None,
            height=dp(0)
        )

        # --- File Path Field ---
        self.file_path = MDTextField(
            text=self.settings["file_import_path"],
            hint_text="Choose file",
            readonly=True,
            size_hint_y=None,
            height=dp(50)
        )
        self.file_path.bind(on_touch_down=self.open_file_picker)

        # --- TTS Fields----
        self.decoder_steps_input = MDTextField(
            text=str(self.settings["max_decoder_steps"]),
            hint_text="(int)",
            size_hint_y=None,
            height=dp(50),
            input_filter='int'
        )

        self.sampling_rate_field = MDTextField(
            text=str(self.settings.get("sampling_rate", 22050)),
            hint_text="Select Sampling Rate",
            readonly=True,
            size_hint_y=None,
            height=dp(50)
        )
        self.sampling_rate_field.bind(on_touch_down=self.open_sampling_rate_menu)

        self.stop_threshold = MDTextField(
            text=str(self.settings["stop_threshold"]),
            hint_text="how confident the model knows it should stop (0 to 1)",
            size_hint_y=None,
            height=dp(50),
            input_filter='float'
        )

        def get_hifigan_config():
            hifigan_config_path = str(self.settings.get("hifigan_config_path"))
            if hifigan_config_path == "hifi_gan/config_v1.json":
                return "v1"
            elif hifigan_config_path == "hifi_gan/config_v1b.json":
                return "v1b"
            else:
                return hifigan_config_path

        self.hifigan_version_field = MDTextField(
            text=get_hifigan_config(),
            hint_text="Select Hifigan Config",
            readonly=True,
            size_hint_y=None,
            height=dp(50)
        )
        self.hifigan_version_field.bind(on_touch_down=self.open_hifigan_version_menu)

        self.hifigan_file_path = MDTextField(
            text=self.settings["hifigan_path"],
            hint_text="Choose file",
            readonly=True,
            size_hint_y=None,
            height=dp(50)
        )
        self.hifigan_file_path.bind(on_touch_down=self.open_hifigan_file_picker)

        self.max_duration = MDTextField(
            text=str(self.settings["max_duration"]),
            hint_text="in second",
            size_hint_y=None,
            height=dp(50),
            input_filter='int'
        )

        self.superres_strength = MDTextField(
            text=str(self.settings["superres_strength"]),
            hint_text="Add sparkle/detail (Might piercing highs, distortion)",
            size_hint_y=None,
            height=dp(50),
            input_filter='int'
        )

        self.use_pronunciation = MDTextField(
            text=str(self.settings.get("use_pronunciation", True)),
            hint_text="Use Pronunciation",
            readonly=True,
            size_hint_y=None,
            height=dp(50)
        )
        self.use_pronunciation.bind(on_touch_down=self.open_use_pronunciation_menu)

        self.denoiser_strength = MDTextField(
            text=str(self.settings["denoiser_strength"]),
            hint_text="Strength of remove hiss/static",
            size_hint_y=None,
            height=dp(50),
            input_filter='int'
        )

        # --- Advanced Fields ---
        self.similarity_input = MDTextField(
            text=str(self.settings["similarity_threshold"]),
            hint_text="0 to 1(float)",
            size_hint_y=None,
            height=dp(50),
            input_filter='float'
        )

        # Save Button
        self.save_button = MDRaisedButton(
            text="Save Settings",
            on_release=self.save_all,
            size_hint_y=None,
            height=dp(50),
            pos_hint={"center_x": 0.5}
        )

        # Tabs
        self.tabs = NoSwipeTabs()
        self.tabs.add_widget(GeneralTab(self, title="General"))
        self.tabs.add_widget(TTSTab(self, title="Tacotron2"))
        self.tabs.add_widget(AdvancedTab(self, title="Advanced"))
        self.tabs.bind(on_tab_switch=self.set_custom_tab_colors)
        self.set_custom_tab_colors(self.tabs, None, None, self.tabs.get_tab_list()[0].text)

        self.add_widget(self.tabs)

        # Always-visible bottom bar
        bottom_wrapper = MDBoxLayout(
            orientation="vertical",
            padding=[dp(20), dp(10)],
            size_hint_y=None,
            height=dp(80)
        )
        bottom_wrapper.add_widget(self.save_button)
        self.add_widget(bottom_wrapper)

    def get_TTS_value(self):
        TTS_model_path = self.file_path.text
        max_decoder_steps = int(self.decoder_steps_input.text)
        sampling_rate = int(self.sampling_rate_field.text)
        stop_threshold = float(self.stop_threshold.text)
        hifigan_config_path = self.get_hifigan_config_path()
        max_duration = int(self.max_duration.text)
        superres_strength = int(self.superres_strength.text)
        use_pronunciation = bool(self.use_pronunciation.text)
        hifigan_path = self.hifigan_file_path.text
        denoiser_strength = int(self.denoiser_strength.text)
        return (TTS_model_path, max_decoder_steps, sampling_rate, stop_threshold, hifigan_config_path, max_duration,
                superres_strength, use_pronunciation, hifigan_path, denoiser_strength)


    def set_custom_tab_colors(self, instance_tabs, instance_tab, instance_tab_label, tab_text):
        for tab in instance_tabs.get_tab_list():
            if hasattr(tab, "text"):
                if tab.text == tab_text:
                    tab.theme_text_color = "Custom"
                    tab.text_color = (1, 1, 1, 1)  # White when active
                else:
                    tab.theme_text_color = "Custom"
                    tab.text_color = (0.7, 0.7, 0.7, 1)  # Light grey for inactive

    def open_theme_menu(self, instance, touch):
        if instance.collide_point(*touch.pos):
            def create_menu(*_):
                if hasattr(self, 'theme_spinner') and self.theme_spinner:
                    self.theme_spinner.dismiss()

                theme_items = [
                    {
                        "text": t,
                        "viewclass": "OneLineListItem",
                        "on_release": lambda x=t: self.set_theme(x)
                    } for t in ["light", "dark"]
                ]

                self.theme_spinner = MDDropdownMenu(
                    caller=self.theme_text,
                    items=theme_items,
                    width_mult=1,
                    max_height=dp(150)
                )

                def set_size_and_pos(_):
                    self.theme_spinner.width = self.theme_text.width

                    # Get absolute position of the textfield
                    x, y = self.theme_text.to_window(
                        self.theme_text.x, self.theme_text.y
                    )
                    self.theme_spinner.pos = (x, y - self.theme_spinner.height + 10)

                Clock.schedule_once(set_size_and_pos, 0.01)
                self.theme_spinner.open()

            Clock.schedule_once(create_menu, 0)


    def set_theme(self, theme):
        self.theme_text.text = theme
        self.app.theme_cls.theme_style = theme.capitalize()
        self.theme_spinner.dismiss()
        self.apply_theme_background()

    def apply_theme_background(self):
        if self.app.theme_cls.theme_style == "Dark":
            new_color = get_color_from_hex("#2A2A2A")  # Softer dark
        else:
            new_color = get_color_from_hex("#FFFFFF")  # Light mode
        self.md_bg_color = new_color
        for tab in self.tabs.get_tab_list():
            if hasattr(tab._context, "container"):
                tab.content.container.md_bg_color = new_color

    def open_music_menu(self, instance, touch):
        if instance.collide_point(*touch.pos):

            def create_menu(*_):
                if hasattr(self, 'music_menu') and self.music_menu:
                    self.music_menu.dismiss()

                music_items = [
                    {
                        "text": name,
                        "viewclass": "OneLineListItem",
                        "on_release": lambda x=name: self.set_music_provider(x)
                    } for name in music_provider_map.values()
                ]

                self.music_menu = MDDropdownMenu(
                    caller=self.music_provider_field,
                    items=music_items,
                    width_mult=1,  # adjust as needed
                    max_height=dp(150)
                )

                def set_size_and_pos(_):
                    self.music_menu.width = self.music_provider_field.width

                    x, y = self.music_provider_field.to_window(
                        self.music_provider_field.x, self.music_provider_field.y
                    )
                    self.music_menu.pos = (x, y - self.music_menu.height + 10)

                Clock.schedule_once(set_size_and_pos, 0.01)
                self.music_menu.open()

            Clock.schedule_once(create_menu, 0)

    def set_music_provider(self, name):
        self.music_provider_field.text = name
        self.music_menu.dismiss()

    def open_file_picker(self, instance, touch):
        if instance.collide_point(*touch.pos):
            system = platform.system()

            # Check if android
            if system == "Linux" and ("ANDROID_ARGUMENT" in os.environ):
                start_path = "/sdcard"
            elif system == "Windows" or "Darwin" or "Linux":
                start_path = os.path.expanduser("~")
            else:
                start_path = "/"
            self.file_manager.show(start_path)

    def select_file_path(self, path):
        allowed_extensions = [".pt", ".pth", ".t7", ""]

        if any(path.lower().endswith(ext) for ext in allowed_extensions):
            self.file_path.text = path
            self.exit_file_manager()
        else:
            toast("Error File Type")

    def exit_file_manager(self, *args):
        self.file_manager.close()

    def open_hifigan_file_picker(self, instance, touch):
        if instance.collide_point(*touch.pos):
            system = platform.system()

            # Check if android
            if system == "Linux" and ("ANDROID_ARGUMENT" in os.environ):
                start_path = "/sdcard"
            elif system == "Windows" or "Darwin" or "Linux":
                start_path = os.path.expanduser("~")
            else:
                start_path = "/"
            self.file_manager.show(start_path)

    def select_hifigan_file_path(self, path):
        allowed_extensions = [".pt", ".pth", ".t7", ""]

        if any(path.lower().endswith(ext) for ext in allowed_extensions):
            self.file_path.text = path
            self.exit_file_manager()
        else:
            toast("Error File Type")

    def exit_hifigan_file_manager(self, *args):
        self.file_manager.close()

    def open_sampling_rate_menu(self, instance, touch):
        if instance.collide_point(*touch.pos):

            def create_menu(*_):
                if hasattr(self, 'sampling_rate_menu') and self.sampling_rate_menu:
                    self.sampling_rate_menu.dismiss()

                items = [
                    {
                        "text": str(rate),
                        "viewclass": "OneLineListItem",
                        "on_release": lambda x=rate: self.set_sampling_rate(x)
                    } for rate in sampling_rates
                ]

                self.sampling_rate_menu = MDDropdownMenu(
                    caller=self.sampling_rate_field,
                    items=items,
                    width_mult=1,
                    max_height=dp(150)
                )

                def set_size_and_pos(_):
                    self.sampling_rate_menu.width = self.sampling_rate_field.width
                    x, y = self.sampling_rate_field.to_window(
                        self.sampling_rate_field.x, self.sampling_rate_field.y
                    )
                    self.sampling_rate_menu.pos = (x, y - self.sampling_rate_menu.height + 10)

                Clock.schedule_once(set_size_and_pos, 0.01)
                self.sampling_rate_menu.open()

            Clock.schedule_once(create_menu, 0)

    def set_sampling_rate(self, name):
        self.sampling_rate_field.text = str(name)
        self.sampling_rate_menu.dismiss()

    def open_use_pronunciation_menu(self, instance, touch):
        if instance.collide_point(*touch.pos):
            def create_menu(*_):
                if hasattr(self, 'use_pronunciation_menu') and self.use_pronunciation_menu:
                    self.use_pronunciation_menu.dismiss()

                items = [
                    {
                        "text": str(value),
                        "viewclass": "OneLineListItem",
                        "on_release": lambda x=value: self.set_use_pronunciation(x)
                    } for value in [True, False]
                ]

                self.use_pronunciation_menu = MDDropdownMenu(
                    caller=self.use_pronunciation,
                    items=items,
                    width_mult=1,
                    max_height=dp(150)
                )

                def set_size_and_pos(_):
                    self.use_pronunciation_menu.width = self.use_pronunciation.width
                    x, y = self.use_pronunciation.to_window(
                        self.use_pronunciation.x, self.use_pronunciation.y
                    )
                    self.use_pronunciation_menu.pos = (x, y - self.use_pronunciation_menu.height + 10)

                Clock.schedule_once(set_size_and_pos, 0.01)
                self.use_pronunciation_menu.open()

            Clock.schedule_once(create_menu, 0)

    def set_use_pronunciation(self, value):
        self.use_pronunciation.text = str(value)
        self.use_pronunciation_menu.dismiss()

    def open_hifigan_version_menu(self, instance, touch):
        if instance.collide_point(*touch.pos):

            def create_menu(*_):
                if hasattr(self, 'hifigan_version_menu') and self.hifigan_version_menu:
                    self.hifigan_version_menu.dismiss()

                items = [
                    {
                        "text": version,
                        "viewclass": "OneLineListItem",
                        "on_release": lambda x=version: self.set_hifigan_version(x)
                    } for version in hifigan_versions
                ]

                self.hifigan_version_menu = MDDropdownMenu(
                    caller=self.hifigan_version_field,
                    items=items,
                    width_mult=1,
                    max_height=dp(150)
                )

                def set_size_and_pos(_):
                    self.hifigan_version_menu.width = self.hifigan_version_field.width
                    x, y = self.hifigan_version_field.to_window(
                        self.hifigan_version_field.x, self.hifigan_version_field.y
                    )
                    self.hifigan_version_menu.pos = (x, y - self.hifigan_version_menu.height + 10)

                Clock.schedule_once(set_size_and_pos, 0.01)
                self.hifigan_version_menu.open()

            Clock.schedule_once(create_menu, 0)

    def set_hifigan_version(self, version):
        self.hifigan_version_field.text = version
        self.hifigan_version_menu.dismiss()


    def check_all_valid(self):
        if not (0 < float(self.similarity_input.text) < 1):
            return False
        if int(self.decoder_steps_input.text) < 0:
            return False
        if not (0 < float(self.stop_threshold.text) < 1):
            return False
        if int(self.max_duration.text) < 0:
            return False
        if int(self.superres_strength.text) < 0:
            return False
        if int(self.denoiser_strength.text) < 0:
            return False
        return True

    def get_hifigan_config_path(self):
        hifigan_version = self.hifigan_version_field.text
        if hifigan_version == hifigan_versions[0]:
            return "hifi_gan/config_v1.json"
        elif hifigan_version == hifigan_versions[1]:
            return "hifi_gan/config_v1b.json"
        else:
            return hifigan_version


    def save_all(self, _instance):
        if not self.check_all_valid():
            toast("Error Input")
            return

        self.settings["theme"] = self.theme_text.text
        self.settings["volume"] = self.volume_slider.value / 100
        self.settings["music_provider"] = music_text_to_id.get(self.music_provider_field.text, 0)
        self.settings["quit_command"] = self.quit_command.text
        self.settings["file_import_path"] = self.file_path.text
        self.settings["similarity_threshold"] = float(self.similarity_input.text)
        self.settings["max_decoder_steps"] = int(self.decoder_steps_input.text)
        self.settings["sampling_rate"] = int(self.sampling_rate_field.text)
        self.settings["stop_threshold"] = float(self.stop_threshold.text)
        self.settings["hifigan_config_path"] = self.get_hifigan_config_path()
        self.settings["hifigan_file_path"] = self.hifigan_file_path.text
        self.settings["max_duration"] = int(self.max_duration.text)
        self.settings["superres_strength"] = int(self.superres_strength.text)
        self.settings["use_pronunciation"] = bool(self.use_pronunciation.text)
        self.settings["denoiser_strength"] = int(self.denoiser_strength.text)
        save_settings(self.settings)
        toast("Saved Config")


class SettingsApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = get_settings().get("theme", "Light").capitalize()
        self.settings_screen = SettingsScreen()
        self.settings_screen.apply_theme_background()
        return self.settings_screen


def open_gui():
    SettingsApp().run()


if __name__ == "__main__":
    open_gui()
