from kivymd.uix.label import MDLabel


class SpaceLabel(MDLabel):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.markup = True
        self.font_style = 'SpaceLabel'
