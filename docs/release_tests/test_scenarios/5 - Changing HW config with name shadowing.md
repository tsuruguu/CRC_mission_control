# 5 - Changing HW config with name shadowing

**Tag:** Configurations

## Check if configuration change occurs correctly when two configurations have widgets with identical names but for different devices (e.g. Dynamixel and Relay).

### Test Preparation

- Grażyna >= 23R2
- Working base station or its mock (simulator)
- Grażyna configuration compliant with the current hardware configuration of the rocket/groundstation
- Available serial port to establish connection with the base station
- Operating system: Windows 10 23H1
- HW configs shadowing names of their device widgets, important that there are shadowed widgets that also have different types from each other

### Test Description

Check if configuration change occurs correctly when two configurations have widgets with identical names but for different devices (e.g. Dynamixel and Relay).

For an example of such two HW configs see device "xd" in these files:
- https://github.com/AGH-Space-Systems/rocket-ground-station/blob/0af00a495b3e22532a2828bacff0691a49f34b23/rocket_ground_station/configs/hardware_configs/develop.yaml
- https://github.com/AGH-Space-Systems/rocket-ground-station/blob/0af00a495b3e22532a2828bacff0691a49f34b23/rocket_ground_station/configs/hardware_configs/trb.yaml

### Test Steps

1. Launch Grażyna with the following parameters: --mock, --debug
2. Load config A
3. Load config B
4. At this point config B should be loaded without trouble, exception or crash.
5. Application component functionality should remain the same as if config B was loaded initially from the start

### Expected Result

The application works correctly after reloading configuration between which device names overlap.

### Test Notes

This test prevents regression related to this issue: https://github.com/AGH-Space-Systems/rocket-ground-station/issues/102