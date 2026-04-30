import unittest

from rocket_ground_station.core.communication import Frame
from rocket_ground_station.core.communication.ids import DataTypeID
from rocket_ground_station.core.communication.protocol import \
    GroundStationProtocol as gp


class TestProtocol(unittest.TestCase):
    def test_if_no_data_decoded(self):
        # Assign
        frame = Frame(destination=1, priority=1, action=1, source=1, device_type=1,
                      device_id=1, data_type=DataTypeID.NO_DATA, operation=1)
        # Act
        data = gp.encode(frame)
        decoded = gp.decode(data)
        # Assert
        self.assertEqual(decoded.payload, frame.payload)

    def test_if_uint8_with_zero_decoded(self):
        # Assign
        payload = (0,)
        frame = Frame(destination=1, priority=1, action=1, source=1, device_type=1,
                      device_id=1, data_type=DataTypeID.UINT8, operation=1, payload=payload)
        # Act
        data = gp.encode(frame)
        decoded = gp.decode(data)
        # Assert
        self.assertEqual(decoded.payload, payload)

    def test_if_uint8_with_value_decoded(self):
        # Assign
        payload = (1,)
        frame = Frame(destination=1, priority=1, action=1, source=1, device_type=1,
                      device_id=1, data_type=DataTypeID.UINT8, operation=1, payload=payload)
        # Act
        data = gp.encode(frame)
        decoded = gp.decode(data)
        # Assert
        self.assertEqual(decoded.payload, payload)

    def test_if_int8_with_zero_decoded(self):
        # Assign
        payload = (0,)
        frame = Frame(destination=1, priority=1, action=1, source=1, device_type=1,
                      device_id=1, data_type=DataTypeID.INT8, operation=1, payload=payload)
        # Act
        data = gp.encode(frame)
        decoded = gp.decode(data)
        # Assert
        self.assertEqual(decoded.payload, payload)

    def test_if_int8_with_value_decoded(self):
        # Assign
        payload = (1,)
        frame = Frame(destination=1, priority=1, action=1, source=1, device_type=1,
                      device_id=1, data_type=DataTypeID.INT8, operation=1, payload=payload)
        # Act
        data = gp.encode(frame)
        decoded = gp.decode(data)
        # Assert
        self.assertEqual(decoded.payload, payload)

    def test_if_int16_with_value_decoded(self):
        # Assign
        payload = (1,)
        frame = Frame(destination=1, priority=1, action=1, source=1, device_type=1,
                      device_id=1, data_type=DataTypeID.INT16, operation=1, payload=payload)
        # Act
        data = gp.encode(frame)
        decoded = gp.decode(data)
        # Assert
        self.assertEqual(decoded.payload, payload)

    def test_if_int16_with_no_data_decoded(self):
        # Assign
        payload = ()
        excpected_decoded_payload = (0,)
        frame = Frame(destination=1, priority=1, action=1, source=1, device_type=1,
                      device_id=1, data_type=DataTypeID.INT16, operation=1, payload=payload)
        # Act
        data = gp.encode(frame)
        decoded = gp.decode(data)
        # Assert
        self.assertEqual(decoded.payload, excpected_decoded_payload)

    def test_if_uint32_with_zero_decoded(self):
        # Assign
        payload = (0,)
        frame = Frame(destination=1, priority=1, action=1, source=1, device_type=1,
                      device_id=1, data_type=DataTypeID.UINT32, operation=1, payload=payload)
        # Act
        data = gp.encode(frame)
        decoded = gp.decode(data)
        # Assert
        self.assertEqual(decoded.payload, payload)

    def test_if_uint32_with_payload_decoded(self):
        # Assign
        payload = (10,)
        frame = Frame(destination=1, priority=1, action=1, source=1, device_type=1,
                      device_id=1, data_type=DataTypeID.UINT32, operation=1, payload=payload)
        # Act
        data = gp.encode(frame)
        decoded = gp.decode(data)
        # Assert
        self.assertEqual(decoded.payload, payload)

    def test_if_float_decoded(self):
        # Assign
        payload = (10.80,)
        frame = Frame(destination=1, priority=1, action=1, source=1, device_type=1,
                      device_id=1, data_type=DataTypeID.FLOAT, operation=1, payload=payload)
        # Act
        data = gp.encode(frame)
        decoded = gp.decode(data)
        # Assert
        self.assertAlmostEqual(decoded.payload[0], payload[0], places=5)

    def test_if_tuple_decoded(self):
        # Assign
        payload = (10, 10)
        frame = Frame(destination=1, priority=1, action=1, source=1, device_type=1,
                      device_id=1, data_type=DataTypeID.INT16X2, operation=1, payload=payload)
        # Act
        data = gp.encode(frame)
        decoded = gp.decode(data)
        # Assert
        self.assertEqual(decoded.payload, payload)

    def test_if_uint_tuple_decoded(self):
        # Assign
        payload = (10, 10)
        frame = Frame(destination=1, priority=1, action=1, source=1, device_type=1,
                      device_id=1, data_type=DataTypeID.UINT16INT16, operation=1, payload=payload)
        # Act
        data = gp.encode(frame)
        decoded = gp.decode(data)
        # Assert
        self.assertEqual(decoded.payload, payload)

    def test_computing_crc(self):
        input_bytes = [b'\x05\xa1\x08A\x00\x01\x00\x00\x00\x00',
                       b'\x05\xa1\x08B0\x01{\x00\x00\x00',
                       b'\x05\x81\tBP\x01\xc8\x01\x00\x00']
        correct_crcs = [b':\x18\x1a\xaa', b'L\r\xa8:', b'\xbc\xd0p\x11']
        for raw_input, crc in zip(input_bytes, correct_crcs):
            self.assertEqual(crc, gp.calculate_crc(raw_input))

    def test_encoding(self):
        frames = [Frame(destination=1, priority=1, action=1, source=1,
                        device_type=1, device_id=1, data_type=0, operation=1, payload=()),
                  Frame(destination=1, priority=1, action=1, source=1,
                        device_type=2, device_id=1, data_type=3, operation=1, payload=(123,)),
                  Frame(destination=1, priority=0, action=3, source=1,
                        device_type=2, device_id=1, data_type=5, operation=1, payload=(456,))]
        frames_bytes = [b'\x05\xa1\x08A\x00\x01\x00\x00\x00\x00:\x18\x1a\xaa',
                        b'\x05\xa1\x08B0\x01{\x00\x00\x00L\r\xa8:',
                        b'\x05\x81\tBP\x01\xc8\x01\x00\x00\xbc\xd0p\x11']
        for frame, frame_bytes in zip(frames, frames_bytes):
            self.assertEqual(frame_bytes, gp.encode(frame))

    def test_decoding(self):
        frames = [Frame(destination=1, priority=1, action=1, source=1,
                        device_type=1, device_id=1, data_type=0, operation=1, payload=()),
                  Frame(destination=1, priority=1, action=1, source=1,
                        device_type=2, device_id=1, data_type=3, operation=1, payload=(123,)),
                  Frame(destination=1, priority=0, action=3, source=1,
                        device_type=2, device_id=1, data_type=5, operation=1, payload=(456,))]
        frames_bytes = [b'\x05\xa1\x08A\x00\x01\x00\x00\x00\x00:\x18\x1a\xaa',
                        b'\x05\xa1\x08B0\x01{\x00\x00\x00L\r\xa8:',
                        b'\x05\x81\tBP\x01\xc8\x01\x00\x00\xbc\xd0p\x11']
        for frame, frame_bytes in zip(frames, frames_bytes):
            self.assertEqual(frame, gp.decode(frame_bytes))


if __name__ == '__main__':
    unittest.main()
