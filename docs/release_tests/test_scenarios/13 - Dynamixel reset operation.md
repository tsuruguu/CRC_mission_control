# 13 - Dynamixel reset operation

**Tag:** Devices

## Check the correctness of sending Dynamixel reset requests (both HW and SW)

### Test Preparation

- Grażyna >= 23R2
- Working base station or its mock (simulator)
- Grażyna configuration compliant with the current hardware configuration of the rocket/groundstation
- Available serial port to establish connection with the base station
- Operating system: Windows 10 23H1

### Test Description

Check the correctness of sending reset requests to Dynamixels.

### Test Steps

1. Launch Grażyna with --debug flag (and --mock if you don't have a base station in test setup)
2. Establish connection with ground station
3. Load configuration containing Dynamixels
4. Press the "RESET DYNAMIXELS HW" button
5. Appropriate frames should be sent and received
6. Press the "RESET DYNAMIXELS SW" button
7. Appropriate frames should be sent and received

### Expected Result

Frames ordering reset of individual boards are sent correctly and an ack confirming the operation request is received.

### Test Notes

None