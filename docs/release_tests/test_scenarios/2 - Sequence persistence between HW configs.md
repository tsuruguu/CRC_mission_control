# 2 - Sequence persistence between HW configs

**Tag:** Sequences

## Check if sequences are not lost after changing hardware configuration and saving other sequences.

### Test Preparation

- Grażyna >= 23R1
- Working base station or its mock (simulator)
- Grażyna configuration compliant with the current hardware configuration of the rocket/groundstation
- Available serial port to establish connection with the base station
- Operating system: Windows 10 23H1

### Test Description

Check if sequences are not lost after changing hardware configuration and saving other sequences.

### Test Steps

1. Launch Grażyna with --mock and --debug flags
2. Load some hardware configuration and create a sequence on it e.g. test_1 and save it
3. Check if the sequence is present in app_config.yaml
4. Load another configuration, preferably very different from the first one
5. A lack of sequences for this configuration should be displayed in the sequence tab
6. Create a new sequence e.g. test_2 and save it
7. Return to the first hardware configuration
8. Check if the test_1 sequence is still displayed in the sequences tab

### Expected Result

Sequences saved for one hardware configuration are not lost after changing hardware configuration and saving new sequences for it.

### Test Notes

This test prevents regression related to the following issue:
https://github.com/AGH-Space-Systems/rocket-ground-station/issues/95