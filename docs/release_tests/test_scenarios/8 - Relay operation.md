# 8 - Relay operation

**Tag:** Devices

## Check the correctness of relay control.

### Test Preparation

- Grażyna >= 23R2
- Working base station or its mock (simulator)
- Grażyna configuration compliant with the current hardware configuration of the rocket/groundstation
- Available serial port to establish connection with the base station
- Operating system: Windows 10 23H1

### Test Description

Check the correctness of relay control.

### Test Steps

1. Launch Grażyna with --debug flag (and --mock if you don't have a base station in test setup)
2. Establish connection with ground station
3. Synchronize the selected relay by pressing its synchronization button
4. Relay synchronization should succeed, appropriate frames should be sent and received
5. Press the "OPEN" button for this relay
6. Relay should be successfully opened, appropriate frames should be sent and received
7. Press the "CLOSE" button for this relay
8. Relay should be successfully closed, appropriate frames should be sent and received

### Expected Result

All operations performed on the relay should be correctly executed and information about their execution should be visible in Grażyna. Frames sent during these operations should have correct structure.

### Test Notes

None