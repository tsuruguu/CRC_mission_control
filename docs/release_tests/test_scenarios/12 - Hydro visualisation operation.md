# 12 - Hydro visualisation operation

**Tag:** Hydro

## Check the correctness of data display by hydro visualization and control through it of device widgets.

### Test Preparation

- Grażyna >= 23R2
- Working base station or its mock (simulator)
- Grażyna configuration compliant with the current hardware configuration of the rocket/groundstation
- Available serial port to establish connection with the base station
- Operating system: Windows 10 23H1

### Test Description

Check the correctness of data display by hydro visualization and control through it of device widgets.

### Test Steps

1. Launch Grażyna with --debug flag (and --mock if you don't have a base station in test setup)
2. Establish connection with ground station
3. Load configuration for TRB
4. Arm all devices with the main arming switch
5. Go to the "HYDRAULICS" tab
6. The visualization should show unknown state on all devices at this point
7. Perform example operations common for devices contained in the visualization
8. Devices should work correctly and show symbols in the visualization adequate for the operation performed on them.
9. Visualization elements assigned to sensors should display operating data from devices assigned to them.

### Expected Result

Hydraulics visualization works correctly, displays data adequate to operations performed through it.

### Test Notes

None