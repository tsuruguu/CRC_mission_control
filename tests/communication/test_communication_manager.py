import unittest
from rocket_ground_station.core.communication import CommunicationManager, Frame, ids


class TestCommunicationManager(unittest.TestCase):
    def setUp(self):
        self.cm = CommunicationManager()

    def create_frame(self, priority):
        # provided ids have no underneath meaning for testcases and given only for examples
        return Frame(
            destination=ids.BoardID.KROMEK,
            priority=priority,
            action=ids.ActionID.SERVICE,
            source=ids.BoardID.GRAZYNA,
            device_type=ids.DeviceID.SERVO,
            device_id=1,
            data_type=ids.DataTypeID.NO_DATA,
            operation=ids.OperationID.SERVO.value.OPEN)

    def test_output_sequence_if_priority_decreases(self):
        #Arrange
        frames = [self.create_frame(int(priority)) for priority in ids.PriorityID]

        #Act
        for frame in frames:
            self.cm.push(frame)

        #Assert
        for priority in ids.PriorityID:
            msg = 'wrong order of frames when priority order decreases'
            self.assertEqual(priority, self.cm.pop().priority, msg)

    def test_output_sequence_if_priority_increases(self):
        #Arrange
        frames = [self.create_frame(int(priority)) for priority in reversed(ids.PriorityID)]

        #Act
        for frame in frames:
            self.cm.push(frame)

        #Assert
        for priority in ids.PriorityID:
            msg = 'wrong order of frames when priority order increases'
            self.assertEqual(priority, self.cm.pop().priority, msg)

    def test_output_order_if_priority_does_not_change(self):
        #Arrange
        frames = [self.create_frame(priority) for priority in [int(ids.PriorityID['HIGH'])] * 3]

        #Act
        for frame in frames:
            self.cm.push(frame)

        #Assert
        for frame in frames:
            msg = 'wrong order of frames when priority does not change'
            self.assertIs(frame, self.cm.pop(), msg)


if __name__ == '__main__':
    unittest.main()
