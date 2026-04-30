from kivy.properties import NumericProperty, ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy_garden.graph import  MeshLinePlot


class LivePlot(BoxLayout):
    graph = ObjectProperty()
    xlabel = StringProperty('N')
    ylabel = StringProperty('Y')
    xs_range = NumericProperty(100)

    def __init__(self, xlabel='X', ylabel='Y', xs_range=100, ymax=100,
                 **kwargs):
        super().__init__(**kwargs)
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.xs_range = xs_range
        self.plot = MeshLinePlot(color=[1, 0, 0, 1], points=[])
        self._paused = True
        self._start_x_coord = self._curr_x_coord
        self.ymax = ymax
        self._points_from_start_count = -1

    def start(self):
        self._paused = False

    def pause(self):
        self._paused = True

    def add_point(self, y):
        x = self._get_x_coord()
        if not self._paused:
            self.graph.remove_plot(self.plot)
            self._update_data(x, y)
            self._recalculate_limits()
            self.graph.add_plot(self.plot)

    def _update_data(self, x, y):
        if len(self.plot.points) == 0:
            self.ymax = 1.1*y
            self.plot.points = [(x, y)]
        elif len(self.plot.points) >= self.xs_range:
            self.plot.points = [*self.plot.points[1:], (x, y)]
        else:
            self.plot.points = [*self.plot.points, (x, y)]

    def _recalculate_limits(self):
        self.graph.xmin = self.plot.points[0][0]
        self.graph.xmax = self.xs_range + self.graph.xmin
        last_y = self.plot.points[-1][1]
        self.graph.ymax = max(1.1 * last_y, self.graph.ymax)

    def _get_x_coord(self):
        # Method left for more easier migration to another values on x axes
        return self._curr_x_coord - self._start_x_coord

    @property
    def _curr_x_coord(self):
        if not self._paused:
            self._points_from_start_count += 1
        return self._points_from_start_count
