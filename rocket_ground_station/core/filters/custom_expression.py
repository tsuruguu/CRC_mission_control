from rocket_ground_station.core.filters.data_filter import DataFilter
import math #pylint: disable=unused-import


class CustomExpression(DataFilter):
    def __init__(self, expression: str):
        self._expression = expression
        self._compiled_expression = eval('lambda x: ' + self._expression) #pylint: disable=eval-used

    def filter(self, x: float) -> float:
        return self._compiled_expression(x)
