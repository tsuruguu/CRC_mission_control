# 4 - Changing HW config

**Tag:** Configurations

## Check if changing hardware configuration occurs correctly and doesn't cause crashes.

### Test Preparation

- Grażyna >= 23R2
- Working base station or its mock (simulator)
- Grażyna configuration compliant with the current hardware configuration of the rocket/groundstation
- Available serial port to establish connection with the base station
- Operating system: Windows 10 23H1

### Test Description

Check if changing hardware configuration occurs correctly and doesn't cause crashes.

### Test Steps

1. Launch Grażyna with parameters: --mock, --debug
2. The default HW config specified in app_config.yaml should be loaded
3. Change the hardware configuration to a different one during Grażyna operation
4. All widgets should be loaded correctly, the application should not crash

### Expected Result

Hardware configuration is changed correctly, the application loaded all widgets correctly and no crash occurred.

### Test Notes

None