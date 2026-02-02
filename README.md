# Sonicare BLE Toothbrush Integration

This integration allows you to connect and monitor your Sonicare BLE toothbrushes in Home Assistant.

## Prerequisites

Before installing this integration, you need:

- **Bluetooth Adapter**: Home Assistant needs access to a Bluetooth adapter
- **Bluetooth Proxy** (recommended): An [ESPHome Bluetooth Proxy](https://esphome.io/components/bluetooth_proxy.html) device for better range and reliability
  - Alternative: Home Assistant server with built-in Bluetooth adapter
- **Supported Toothbrush**: Modern Philips Sonicare toothbrush with Bluetooth connectivity (2017+)
  - Look for models that advertise "Bluetooth" or work with the Philips Sonicare app

### Setting up a Bluetooth Proxy

If your Home Assistant server is far from your bathroom, a Bluetooth proxy will provide better connectivity:

1. Get an ESP32 device (ESP32-C3, ESP32-S3, or regular ESP32)
2. Flash it with ESPHome Bluetooth Proxy firmware
3. Add it to Home Assistant
4. The toothbrush will automatically connect through the proxy

For detailed instructions, see: [ESPHome Bluetooth Proxy Documentation](https://esphome.io/components/bluetooth_proxy.html)

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
