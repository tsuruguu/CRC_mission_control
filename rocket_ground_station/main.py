# nuitka-project: --include-data-dir=layouts=layouts
# nuitka-project: --include-data-dir=assets=assets

import os

os.environ['KIVY_NO_ARGS'] = '1'
os.environ['KIVY_METRICS_DENSITY'] = '1'
import traceback
from os.path import dirname, join
from argparse import ArgumentParser
from datetime import datetime
from pathlib import Path
import sys
import logging

import kivy
from kivymd.app import MDApp
from kivy.resources import resource_add_path
from kivy.core.window import Window
from kivy.lang.builder import Builder
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.base import ExceptionManager, ExceptionHandler
from kivy.core.text import LabelBase
from kivy.config import Config
from rocket_ground_station.components.popups import Message

if hasattr(sys, '_MEIPASS'):
    # pylint: disable=protected-access, no-member
    resource_add_path(os.path.join(sys._MEIPASS, 'rocket_ground_station'))

from rocket_ground_station.core.configs import AppConfig
from rocket_ground_station.components.menu import Menu
from rocket_ground_station.components.popups import BinaryQuestion
from rocket_ground_station.components.tabs import Tab

kivy.require("2.1.0")
Builder.load_file(join(dirname(__file__), 'layouts/groundstation.kv'))


class GroundStation(MDApp):
    """
    Starts all core processes in the Ground Station.
    """

    def __init__(self, *args, debug_mode: bool = False, mock_mode: bool = False, **kwargs):
        super().__init__(*args, **kwargs)
        self.menu: Menu = None
        self.setup_loggers()
        if not debug_mode:
            ExceptionManager.add_handler(SpaceExceptionHandler())
        self.mock_mode = mock_mode

    def _setup_main_logger(self):
        logger_main = logging.getLogger("main")
        logger_main.setLevel(logging.DEBUG)
        logger_main.propagate = False

        fmt = '[%(asctime)s] [%(levelname)s] [MAIN] %(message)s'
        log_formatter = logging.Formatter(fmt=fmt)

        log_file_path = Path(sys.argv[0]).resolve().parent.joinpath('logs')
        Path(log_file_path).mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(
            join(dirname(__file__),
                 'logs',
                 str(datetime.now().strftime('%Y_%m_%d_%H_%M_%S')) + ".log")
        )

        console_handler = logging.StreamHandler(sys.stdout)

        file_handler.setFormatter(log_formatter)
        console_handler.setFormatter(log_formatter)
        logger_main.addHandler(file_handler)
        logger_main.addHandler(console_handler)

    def _setup_sequences_logger(self):
        logger_sequences = logging.getLogger("sequences")
        logger_sequences.setLevel(logging.DEBUG)
        logger_sequences.propagate = False

        fmt = '[%(asctime)s] [%(levelname)s] [SEQUENCES] %(message)s'
        log_formatter = logging.Formatter(fmt=fmt)

        log_file_path = Path(sys.argv[0]).resolve().parent.joinpath('logs').joinpath('sequences')
        Path(log_file_path).mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(
            join(dirname(__file__),
                 'logs',
                 'sequences',
                 str(datetime.now().strftime('%Y_%m_%d_%H_%M_%S')) + ".log")
        )

        console_handler = logging.StreamHandler(sys.stdout)

        file_handler.setFormatter(log_formatter)
        console_handler.setFormatter(log_formatter)
        logger_sequences.addHandler(file_handler)
        logger_sequences.addHandler(console_handler)

    def setup_loggers(self):
        self._setup_main_logger()
        self._setup_sequences_logger()

    def apply_material_theming(self, dark_mode: bool) -> None:
        self.theme_cls.primary_palette = 'Teal'
        if dark_mode:
            self.theme_cls.theme_style = 'Dark'
            # fix for wrong colors defined in kivymd
            self.theme_cls.colors["Dark"] = {
                "StatusBar": "000000",  # bg_darkest
                "AppBar": "181818",  # bg_dark
                "Background": "1f1f1f",  # bg_normal
                "CardsDialogs": "262626",  # bg_light
                "FlatButtonDown": "999999",
            }
        else:
            # TODO: verify light theme
            self.theme_cls.theme_style = 'Light'

    def load_fonts(self, font_name: str, font_scaling: float) -> dict:
        font_dir = join(dirname(__file__), 'assets', 'fonts')
        LabelBase.register(
            name=f"{font_name}_regular",
            fn_regular=join(font_dir, f'{font_name}_regular.ttf'),
        )
        LabelBase.register(
            name=f"{font_name}_bold",
            fn_regular=join(font_dir, f'{font_name}_bold.ttf'),
        )
        LabelBase.register(
            name=f"{font_name}_italic",
            fn_regular=join(font_dir, f'{font_name}_italic.ttf'),
        )
        LabelBase.register(
            name=f"{font_name}_light",
            fn_regular=join(font_dir, f'{font_name}_light.ttf'),
        )
        LabelBase.register(
            name='RobotoMono_regular',
            fn_regular=join(font_dir, 'RobotoMono-Regular.ttf'),
        )
        self.theme_cls.font_styles = {
            'SpaceLabel': ['space_bold', round(18 * font_scaling), False, 0.30],
            'SpaceTitleLabel': ['space_bold', round(24 * font_scaling), False, 0.15],
            'SpaceTipLabel': ['space_bold', round(18 * font_scaling), False, 0.30],
            'SpaceTableHeaderLabel': ['space_bold', round(20 * font_scaling), False, 0.30],
            'H1': ['space_regular', round(96 * font_scaling), False, -1.5],
            'H2': ['space_regular', round(60 * font_scaling), False, -0.5],
            'H3': ['space_bold', round(48 * font_scaling), False, 0],
            'H4': ['space_bold', round(34 * font_scaling), False, 0.25],
            'H5': ['space_bold', round(24 * font_scaling), False, 0],
            'H6': ['space_bold', round(20 * font_scaling), False, 0.15],
            'Subtitle1': ['space_bold', round(16 * font_scaling), False, 0.15],
            'Subtitle2': ['space_bold', round(14 * font_scaling), False, 0.1],
            'Body1': ['space_bold', round(16 * font_scaling), False, 0.5],
            'Body2': ['space_bold', round(14 * font_scaling), False, 0.25],
            'Button': ['space_bold', round(16 * font_scaling), True, 1.5],
            'Caption': ['space_bold', round(12 * font_scaling), False, 0.4],
            'Overline': ['space_bold', round(10 * font_scaling), True, 1.5],
            'Icon': ['Icons', round(24 * font_scaling), False, 0],
            # That 1.15 multiplier makes it so logger font scales slightly differently for better readability
            'FrameLogger': ['RobotoMono_regular',
                            round(17 * font_scaling * (1.15 if font_scaling < 1 else 1)),
                            False, 0],
        }

        return {'regular': join(font_dir, f'{font_name}_regular.ttf'),
                'bold': join(font_dir, f'{font_name}_bold.ttf'),
                'italic': join(font_dir, f'{font_name}_italic.ttf'),
                'light': join(font_dir, f'{font_name}_light.ttf')}

    def build(self) -> Widget:
        """
        Preconfigures kivy env and builds the main widget of the app based on a config file.
        :return: the main widget of the app
        """
        AppConfig('grazyna_app_config.yaml', Tab.implemented_tabs)
        if AppConfig().is_invalid:
            return Label(text=f'Invalid config file {AppConfig().filename} '
                              f'has been loaded: {AppConfig().error_message}')
        self.configure_kivy()
        Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
        Config.set('kivy', 'window_icon', 'path/to/icon.ico')
        self.apply_material_theming(AppConfig().dark_mode)
        self.fonts = self.load_fonts(AppConfig().font_name, AppConfig().font_scale)
        self.icon = join(dirname(__file__), 'assets', 'icon.png')
        self.menu = Menu(self.mock_mode)
        return self.menu

    def configure_kivy(self) -> None:
        """
        Sets the kivy properties configured by the app config
        """
        if AppConfig().fullscreen:
            Window.fullscreen = 'auto'
        else:
            Window.fullscreen = False
            Window.maximize()
        Window.bind(on_request_close=self.on_request_close)

    def on_request_close(self, *args, **kwargs) -> bool:
        """
        Called when application is about to be closed. Shows a popup for confirmation.
        :return: returns True to prevent the application from closing automatically
        """
        BinaryQuestion('Are you sure you want to leave?', self.on_close_answer)
        return True

    def on_close_answer(self, close_confirmed: bool) -> None:
        """
        Called by the popup when the application is about to be closed.
        :param close_confirmed: True if user has confirmed application close
        """
        if close_confirmed:
            self.menu.on_close()
            self.stop()


class SpaceExceptionHandler(ExceptionHandler):
    """
    Catches all exceptions and sends them to logger
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.main_logger = logging.getLogger("main")
        self.traceback_logger = logging.getLogger("tracebacks")
        self.traceback_logger.setLevel(logging.DEBUG)
        log_file_path = Path(sys.argv[0]).resolve().parent.joinpath('logs/tracebacks')
        Path(log_file_path).mkdir(parents=True, exist_ok=True)
        self.traceback_logger.addHandler(
            logging.FileHandler(
                join(dirname(__file__),
                     'logs',
                     'tracebacks',
                     str(datetime.now().strftime('%Y_%m_%d_%H_%M_%S')) + '.log')
            )
        )
        self._popup_shown = False

    def handle_exception(self, exception: Exception):
        if isinstance(exception, KeyboardInterrupt):
            return ExceptionManager.RAISE

        exc = traceback.format_exception(type(exception), exception, exception.__traceback__)
        self.traceback_logger.error(''.join(exc))
        self.main_logger.error(f'{type(exception).__name__} was raised: {exception}')

        if not self._popup_shown:
            message_content = ('An error occurred that has left the application in undefined state. '
                               'The application should be restarted now '
                               'but in order to not interrupt your workflow it will remain open. '
                               'Please bear in mind that from now on '
                               'any operation you perform may have an unexpected outcome.'
                               '\n\nPlease restart the application as soon as you can.'
                               "\n\nThis message won't appear again in this application session.")

            Message('Undefined application state', message_content)
            self._popup_shown = True

        return ExceptionManager.PASS


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--mock', action='store_true')
    cl_args = parser.parse_args()
    GroundStation(debug_mode=cl_args.debug, mock_mode=cl_args.mock).run()
