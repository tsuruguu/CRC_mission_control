# 1 - Ground station serial port connection

**Tag:** Communication

## Grażyna establishes connection with the base station and exchanges frames with it

### Test Preparation

- Grażyna >= 23R2
- Working base station or its mock (simulator)
- Grażyna configuration compliant with the current hardware configuration of the rocket/groundstation
- Available serial port to establish connection with the base station
- Operating system: Windows 10 23H1

### Test Description

Grażyna establishes connection with the base station and exchanges frames with it.

### Test Steps

1. Launch Grażyna without additional CLI parameters
2. Press the switch to establish connection with ground station
3. Select the serial port and set the established baudrate
4. Start connection with the base station
5. Arm all devices via the arming switch
6. Wait to receive synchronization frames from Grażyna

### Expected Result

Connection establishment succeeds, Grażyna sends synchronization frames to the base station and receives frames sent by the base station (regardless of whether ACK or NACK, etc.)

### Test Notes

None