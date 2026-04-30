# 11 - Selective arming operation

**Tag:** Devices

## Check the correctness of selective arming buttons for individual devices

### Test Preparation

- Grażyna >= 23R2
- Working base station or its mock (simulator)
- Grażyna configuration compliant with the current hardware configuration of the rocket/groundstation
- Available serial port to establish connection with the base station
- Operating system: Windows 10 23H1

### Test Description

Check the correctness of selective arming buttons for individual devices

### Test Steps

1. Launch Grażyna with --debug flag (and --mock if you don't have a base station in test setup)
2. Establish connection with ground station
3. Do not use the main arming switch
4. By default all devices should be disarmed (their device cards should be disabled, i.e. grayed out and unclickable, the device card should show a button with a closed lock icon)
5. Select one of the devices and press the closed lock button
6. At this moment the device card should become enabled (no longer grayed out and should be clickable)
7. Perform several common operations for this specific device, e.g. open and close
8. Check if the operation passed correctly

### Expected Result

The selective arming system works and does not introduce unwanted side effects on application operation.

### Test Notes

None