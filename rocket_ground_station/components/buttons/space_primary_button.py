from kivymd.uix.button import MDFlatButton


class SpacePrimaryButton(MDFlatButton):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_disabled(self, instance_button, disabled_value: bool) -> None:
        # weird bug with disabled button and border
        self.line_width = 0.001 if disabled_value else 1.1
