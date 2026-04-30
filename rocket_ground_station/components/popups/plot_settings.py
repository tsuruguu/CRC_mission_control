from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup

from rocket_ground_station.components.live_plot import LivePlot
from rocket_ground_station.components.popups.message import Message


class PlotSettings(Popup):
    device_feeds_spinner = ObjectProperty()
    ylabel = ObjectProperty()

    def __init__(self, device, on_plot_created, **kwargs):
        super().__init__(**kwargs)
        self.device = device
        self.on_plot_created = on_plot_created
        if not device.feed_ids:
            Message(title='No data for plot',
                    message='There are no available feeds for this device')
            self.dismiss()
        else:
            self.feeds = {
                feed.name: feed.last_received_value for feed in device.feed_ids}
            self.device_feeds_spinner.values = self.feeds.keys()
            self.open()

    def create_plot(self):
        selected_feed_id = self.feeds[self.device_feeds_spinner.text]
        plot = LivePlot(ylabel=self.ylabel.text)
        self.device.subscribe(selected_feed_id, plot.add_point)
        self.on_plot_created(plot)
        self.dismiss()
