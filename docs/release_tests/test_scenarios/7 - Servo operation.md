# 7 - Servo operation

**Tag:** Devices

## Check the correctness of servo control.

### Test Preparation

- Grażyna >= 23R2
- Working base station or its mock (simulator)
- Grażyna configuration compliant with the current hardware configuration of the rocket/groundstation
- Available serial port to establish connection with the base station
- Operating system: Windows 10 23H1

### Test Description

Check the correctness of servo control.

### Test Steps

1. Launch Grażyna with --debug flag (and --mock if you don't have a base station in test setup)
2. Establish connection with ground station
3. Synchronize the selected servo by pressing its synchronization button
4. Servo synchronization should succeed, appropriate frames should be sent and received
5. Press the "OPEN" button for this servo
6. Servo should be successfully opened, appropriate frames should be sent and received
7. Press the "CLOSE" button for this servo
8. Servo should be successfully closed, appropriate frames should be sent and received
9. Use the "SET" button to set the servo to any custom position in the range between open_pos and closed_pos.
10. Servo should be successfully set to custom position, appropriate frames should be sent and received
11. Use the "SET" button to set the servo to any custom position exceeding open_pos.
12. A popup requiring operation confirmation should be shown. Confirm the operation.
13. Servo should be successfully set to custom position, appropriate frames should be sent and received. This position should become the new open_pos
14. Use the "SET" button to set the servo to any custom position exceeding closed_pos.
15. A popup requiring operation confirmation should be shown. Confirm the operation.
16. Servo should be successfully set to custom position, appropriate frames should be sent and received. This position should become the new closed_pos

### Expected Result

All operations performed on the servo should be correctly executed and information about their execution should be visible in Grażyna. Frames sent during these operations should have correct structure.

### Test Notes

None