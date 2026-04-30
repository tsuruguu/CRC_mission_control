import unittest
from typing import Any
from rocket_ground_station.core.communication import Frame, ids


class TestFrame(unittest.TestCase):
    def setUp(self):
        self.single_value_payload_types = [ids.DataTypeID.INT32,
                                           ids.DataTypeID.UINT32,
                                           ids.DataTypeID.UINT16,
                                           ids.DataTypeID.UINT8,
                                           ids.DataTypeID.INT16,
                                           ids.DataTypeID.INT8,
                                           ids.DataTypeID.FLOAT]
        self.not_single_value_payload_types = [
            ids.DataTypeID.INT16X2,
            ids.DataTypeID.UINT16INT16,
        ]

    def test_if_data_returns_single_value_when_expected(self):
        for data_type in self.single_value_payload_types:
            with self.subTest(data_type=data_type):
                # Assign
                payload = (1,)
                frame = self.create_frame(data_type, payload)
                # Act
                frame_data = frame.data
                # Assert
                self.assertEqual(frame_data, payload[0])

    def test_if_frame_returns_tuple_when_payload_is_not_single_value_type(self):
        for data_type in self.not_single_value_payload_types:
            with self.subTest(data_type=data_type):
                # Assign
                payload = (1, 0)
                frame = self.create_frame(data_type, payload)
                # Act
                frame_data = frame.data
                # Assert
                self.assertEqual(frame_data, payload)

    def test_if_frame_throws_exception_when_field_is_not_castable_to_int(self):
        # Assign
        not_castable_value = 'not_castable_value'
        # Assert
        with self.assertRaises(AssertionError):
            self.create_frame(data_type=not_castable_value)

    def test_if_frame_throws_exception_when_payload_has_more_values_then_declared_in_datatype(self):
        # Assign
        payload = (1, 1, 1)
        for data_type in self.single_value_payload_types:
            with self.subTest(data_type=data_type):
                # Act, Assert
                with self.assertRaises(AssertionError):
                    self.create_frame(data_type, payload)

    def test_if_frame_not_throws_exception_when_payload_matches_data_type(self):
        # Assign
        payload = (1,)
        for data_type in self.single_value_payload_types:
            with self.subTest(data_type=data_type):
                # Act
                try:
                    self.create_frame(data_type, payload)
                except AssertionError:
                    # Assert
                    self.fail(
                        f"Frame with datatype {data_type.name} should not fail for payload {payload} ")

    def test_if_frame_assignes_default_value_when_payload_kwarg_is_not_passed(self):
        # Assign, Act
        frame = Frame(
            destination=ids.BoardID.KROMEK,
            priority=1,
            action=ids.ActionID.SERVICE,
            source=ids.BoardID.GRAZYNA,
            device_type=ids.DeviceID.SERVO,
            device_id=1,
            data_type=ids.DataTypeID.INT32,
            operation=ids.OperationID.SERVO.value.OPEN,
        )
        default_payload = (0,)
        # Assert
        self.assertTupleEqual(frame.payload, default_payload)

    def test_if_frame_casts_to_int_all_frame_fields_except_payload(self):
        # Assign
        frame = self.create_frame(ids.DataTypeID.INT32)
        for value in {f: v for f, v in vars(frame).items() if f != 'payload'}.values():
            with self.subTest(value=value):
                self.assertIs(type(value), int)

    def test_if_frame_patterns_work_correctly(self):
        frame = Frame(destination=ids.BoardID.KROMEK,
                      priority=1,
                      action=ids.ActionID.SERVICE,
                      source=ids.BoardID.GRAZYNA,
                      device_type=ids.DeviceID.SERVO,
                      device_id=1,
                      data_type=ids.DataTypeID.NO_DATA,
                      operation=ids.OperationID.SERVO.value.OPEN,
                      payload=tuple())

        valid_pattern_1 = Frame(destination=ids.BoardID.KROMEK,
                              priority=Any,
                              action=Any,
                              source=Any,
                              device_type=Any,
                              device_id=Any,
                              data_type=Any,
                              operation=Any,
                              payload=Any,
                              pattern=True)

        valid_pattern_2 = Frame(destination=ids.BoardID.KROMEK,
                                priority=Any,
                                action=Any,
                                source=Any,
                                device_type=ids.DeviceID.SERVO,
                                device_id=Any,
                                data_type=Any,
                                operation=Any,
                                payload=Any,
                                pattern=True)

        invalid_pattern_1 = Frame(destination=ids.BoardID.STASZEK,
                                  priority=Any,
                                  action=Any,
                                  source=Any,
                                  device_type=Any,
                                  device_id=Any,
                                  data_type=Any,
                                  operation=Any,
                                  payload=Any,
                                  pattern=True)

        invalid_pattern_2 = Frame(destination=ids.BoardID.KROMEK,
                                  priority=Any,
                                  action=Any,
                                  source=Any,
                                  device_type=ids.DeviceID.DYNAMIXEL,
                                  device_id=Any,
                                  data_type=Any,
                                  operation=Any,
                                  payload=Any,
                                  pattern=True)

        self.assertTrue(frame.match_pattern(valid_pattern_1))
        self.assertTrue(frame.match_pattern(valid_pattern_2))
        self.assertFalse(frame.match_pattern(invalid_pattern_1))
        self.assertFalse(frame.match_pattern(invalid_pattern_2))

    def create_frame(self, data_type=ids.DataTypeID.NO_DATA, payload=(1,)):
        # provided ids have no underneath meaning for testcases and given only for examples
        return Frame(
            destination=ids.BoardID.KROMEK,
            priority=1,
            action=ids.ActionID.SERVICE,
            source=ids.BoardID.GRAZYNA,
            device_type=ids.DeviceID.SERVO,
            device_id=1,
            data_type=data_type,
            operation=ids.OperationID.SERVO.value.OPEN,
            payload=payload
        )


if __name__ == '__main__':
    unittest.main()
