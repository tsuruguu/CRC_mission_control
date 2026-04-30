# 3 - Sequence upload

**Tag:** Sequences

## Grażyna correctly sends sequence to the rocket.

### Test Preparation

- Grażyna >= 23R2
- Working base station or its mock (simulator)
- Grażyna configuration compliant with the current hardware configuration of the rocket/groundstation
- Available serial port to establish connection with the base station
- Operating system: Windows 10 23H1

### Test Description

Grażyna correctly sends sequence to the rocket.

### Test Steps

1. Launch Grażyna without additional CLI parameters
2. Establish connection with the base station
3. Arm all devices
4. Go to the "SEQUENCES" tab
5. Select a sequence from the list
6. Press the "SEND" button
7. Display a window informing about progress
8. Display a window informing about successful upload

### Expected Result

Sequence sending starts correctly. The sending process proceeds without problems, the sequence is accepted by the rocket (receiving SACK frames). The entire sequence was sent to the rocket.

### Test Notes

This test prevents regression related to the following issue:
https://github.com/AGH-Space-Systems/rocket-ground-station/issues/93