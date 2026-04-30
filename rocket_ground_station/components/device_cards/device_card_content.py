from kivymd.uix.boxlayout import MDBoxLayout


class DeviceCardContent(MDBoxLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def requires_large_card(self) -> bool:
        return False

    @property
    def is_excluded_from_arming(self) -> bool:
        return False

    @property
    def is_excluded_from_syncing(self) -> bool:
        return False

    def handle_widget_refreshes(self):
        pass
