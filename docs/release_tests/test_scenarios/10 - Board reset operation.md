# 10 - Board reset operation

**Tag:** Devices

## Reset devices correctly send reset requests to boards.

### Test Preparation

- Grażyna >= 23R2
- Working base station or its mock (simulator)
- Grażyna configuration compliant with the current hardware configuration of the rocket/groundstation
- Available serial port to establish connection with the base station
- Operating system: Windows 10 23H1

### Test Description

Check the correctness of sending reset requests to boards.

### Test Steps

1. Launch Grażyna with --debug flag (and --mock if you don't have a base station in test setup)
2. Establish connection with ground station
3. Load configuration containing reset devices
4. Press the "RESET CZAPLA" button
5. Appropriate frames should be sent and received
6. Press the "RESET STASZEK" button
7. Appropriate frames should be sent and received
8. Press the "RESET KROMEK" button
9. Appropriate frames should be sent and received

### Expected Result

Frames ordering reset of individual boards are sent correctly and an ack confirming the operation request is received.

### Test Notes

None