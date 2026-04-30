from kivy.properties import BooleanProperty, ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout

from rocket_ground_station.components.popups import PlotSettings
from rocket_ground_station.components.live_plot import LivePlot


class PlotContainer(BoxLayout):

    device = ObjectProperty()
    plot_area = ObjectProperty()
    possible_plot_transition = StringProperty('Pause plotting')
    toolbar = ObjectProperty()
    add_plot_btn = ObjectProperty()
    toggle_plot_state_btn = ObjectProperty()
    toggle_btn_visible = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._plotting = True
        self.plot: LivePlot = None

    def on_add_plot_press(self):
        PlotSettings(self.device, self.on_plot_created)

    def on_toggle_plot_state_press(self):
        if hasattr(self, 'plot'):
            if self._plotting:
                self.plot.pause()
            else:
                self.plot.start()
            self._plotting = not self._plotting
            self.possible_plot_transition = 'Pause plotting' if self._plotting else 'Start plotting'

    def on_plot_created(self, created_plot: LivePlot):
        self.toolbar.remove_widget(self.add_plot_btn)
        self.plot = created_plot
        self.toggle_btn_visible = True
        self.plot_area.add_widget(created_plot)
