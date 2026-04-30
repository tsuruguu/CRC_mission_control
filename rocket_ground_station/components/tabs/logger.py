import logging
from kivy.properties import ObjectProperty
from rocket_ground_station.core.communication.ids import LogLevel
from rocket_ground_station.components.tabs.tab import Tab


class Logger(Tab, logging.Handler):
    """
    Implements a tab that allows user to display messages and events.
    """
    logs = ObjectProperty()
    log_level_dropdown = ObjectProperty()
    log_level = ObjectProperty(LogLevel.INFO, options=LogLevel, rebind=True)

    def __init__(self, **tab_kwargs) -> None:
        super().__init__(**tab_kwargs)
        self.log_level_dropdown.items = [lvl.name for lvl in LogLevel]
        # TODO: add debug icon
        self.log_level_dropdown.icons = ['information',
                                         'information',
                                         'alert',
                                         'alert-octagon',
                                         'close-octagon']
        self._logger.info('Rocket Ground Station for AGH Space Systems 25.5.0')
        self._logger.info('Logger tab initialized')

    def emit(self, record: logging.LogRecord) -> None:
        """
        Called when a message is logged.
        :param level: how important the message is (one of 'DEBUG', 'INFO', 'WARN' or 'ERR')
        :param timestamp: time when the message was logged
        :param message: message that is logged
        """
        timestamp = record.asctime
        level = LogLevel(record.levelno)
        message = record.msg
        if self.log_level <= level:
            if level == LogLevel.ERROR:
                log = ''.join(('[color=878a8c][', timestamp,'] [', level.name, '][/color] [color=e0525c][b]',
                               message, '[/b][/color]', '\n'))
            elif level == LogLevel.WARNING:
                log = ''.join(('[color=878a8c][', timestamp,'] [', level.name, '][/color] [color=dbc837][b]',
                               message, '[/b][/color]', '\n'))
            else:
                log = ''.join(
                    ('[color=878a8c][', timestamp,'] [', level.name, '][/color] ', message, '\n'))

            self.logs.text += log
