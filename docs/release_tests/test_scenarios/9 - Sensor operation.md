# 9 - Sensor operation

**Tag:** Devices

## Check if sensors correctly report assigned data.

### Test Preparation

- Grażyna >= 23R2
- Working base station or its mock (simulator)
- Grażyna configuration compliant with the current hardware configuration of the rocket/groundstation
- Available serial port to establish connection with the base station
- Operating system: Windows 10 23H1

### Test Description

Check if sensors correctly report assigned data.

### Test Steps

1. Launch Grażyna with --debug flag (and --mock if you don't have a base station in test setup)
2. Establish connection with ground station
3. Check if sensor widgets correctly display data

### Expected Result

Sensor widgets correctly display data for devices configured for them.

### Test Notes

None