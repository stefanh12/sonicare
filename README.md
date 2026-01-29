# Sonicare BLE Toothbrush Integration

This integration allows you to connect and monitor your Sonicare BLE toothbrushes in Home Assistant.

## Installation

### HACS (Recommended)

1. Make sure you have [HACS](https://hacs.xyz/) installed in your Home Assistant instance
2. Add this repository as a custom repository in HACS:
   - Go to HACS → Integrations
   - Click the three dots in the top right corner
   - Select "Custom repositories"
   - Add the repository URL: `https://github.com/stefanh12/sonicare`
   - Select category: "Integration"
   - Click "Add"
3. Click "Install" on the Sonicare integration
4. Restart Home Assistant
5. Go to Settings → Devices & Services
6. Click "Add Integration" and search for "Sonicare"
7. Follow the configuration steps

### Manual Installation

1. Copy the `custom_components/sonicare_bletb` directory to your Home Assistant's `custom_components` directory
2. Restart Home Assistant
3. Go to Settings → Devices & Services
4. Click "Add Integration" and search for "Sonicare"
5. Follow the configuration steps

## Features

- Real-time monitoring of toothbrush battery level
- Track brushing sessions
- Monitor brushing time
- View toothbrush state and mode

## Credits

This integration is based on the original work by [@GrumpyMeow](https://github.com/GrumpyMeow) from the [sonicare-ble-hacs](https://github.com/GrumpyMeow/sonicare-ble-hacs) repository.

This integration also includes code from the [oralb-ble](https://github.com/Bluetooth-Devices/oralb-ble) library by J. Nick Koston (@bdraco) and contributors from the Bluetooth-Devices organization.
