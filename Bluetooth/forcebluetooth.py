
import subprocess
import re
import sys
import time


def run_command(args, timeout=30):
    """Run a Bluetooth command and return its output."""
    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return "Command timed out."
    except FileNotFoundError:
        print("Error: bluetoothctl is not installed.")
        sys.exit(1)


def check_bluetooth():
    """Check whether a Bluetooth controller is available."""
    output = run_command(["bluetoothctl", "list"])

    if "Controller " not in output:
        print("No Bluetooth controller found.")
        print("Check your Bluetooth adapter and Raspberry Pi OS.")
        return False

    print("Bluetooth controller found.")
    return True


def scan_devices():
    """Scan for nearby Bluetooth devices."""
    print("\nScanning for Bluetooth devices...")
    print("Please wait 15 seconds.\n")

    # Power on the adapter and enable discovery.
    run_command(["bluetoothctl", "power", "on"])
    run_command(["bluetoothctl", "agent", "on"])
    run_command(["bluetoothctl", "default-agent"])

    output = run_command(
        ["bluetoothctl", "--timeout", "15", "scan", "on"],
        timeout=22
    )

    # Get devices known to BlueZ from the scan.
    devices_output = run_command(
        ["bluetoothctl", "devices"],
        timeout=10
    )

    devices = {}
    for line in devices_output.splitlines():
        match = re.search(
            r"Device\s+([0-9A-Fa-f:]{17})\s+(.+)",
            line
        )
        if match:
            mac = match.group(1).upper()
            name = match.group(2).strip()
            devices[mac] = name

    # Also collect device names from the scan output.
    for line in output.splitlines():
        match = re.search(
            r"Device\s+([0-9A-Fa-f:]{17})\s+(.+)",
            line
        )
        if match:
            mac = match.group(1).upper()
            name = match.group(2).strip()
            devices[mac] = name

    return devices


def select_device(devices):
    """Display the discovered devices and ask the user to select one."""
    if not devices:
        print("\nNo devices found.")
        print("Make sure the other device is discoverable and nearby.")
        return None

    device_list = list(devices.items())

    print("\nDiscovered Bluetooth devices:")
    print("-" * 55)

    for index, (mac, name) in enumerate(device_list, start=1):
        print(f"{index}. {name} [{mac}]")

    print("0. Cancel")

    while True:
        choice = input("\nSelect a device number: ").strip()

        if choice == "0":
            return None

        if choice.isdigit():
            index = int(choice)
            if 1 <= index <= len(device_list):
                return device_list[index - 1]

        print("Invalid selection. Try again.")


def connect_device(device):
    """Attempt to connect to the selected Bluetooth device."""
    mac, name = device

    print(f"\nSelected: {name}")
    print(f"Address:  {mac}")

    confirm = input("Attempt connection? (y/n): ").strip().lower()
    if confirm != "y":
        print("Connection cancelled.")
        return

    print("\nAttempting Bluetooth connection...")

    # Pairing may be required before a connection can succeed.
    output = run_command(
        ["bluetoothctl", "connect", mac],
        timeout=35
    )
    print(output)

    if "Connection successful" in output:
        print(f"\nConnected to {name} successfully!")
        return

    print("\nConnection was not successful.")
    print("Possible reasons:")
    print("- The device is not accepting connections.")
    print("- Pairing or authentication is required.")
    print("- The device does not support the requested connection.")
    print("- The device moved out of range.")

    paired = input("Try pairing first? (y/n): ").strip().lower()

    if paired == "y":
        print("\nAttempting pairing...")
        pair_output = run_command(
            ["bluetoothctl", "pair", mac],
            timeout=60
        )
        print(pair_output)

        if "Pairing successful" in pair_output:
            run_command(["bluetoothctl", "trust", mac])
            print("\nRetrying connection...")
            retry_output = run_command(
                ["bluetoothctl", "connect", mac],
                timeout=35
            )
            print(retry_output)

            if "Connection successful" in retry_output:
                print(f"\nConnected to {name} successfully!")
                return

        print("\nPairing or reconnection did not succeed.")
        print("Try pairing interactively with: bluetoothctl")
        print("Then use: pair " + mac)
        print("Follow any prompts and try: connect " + mac)


def main():
    print("=" * 45)
    print(" Raspberry Pi Bluetooth Device Connector")
    print("=" * 45)

    if not check_bluetooth():
        return

    devices = scan_devices()
    selected = select_device(devices)

    if selected is not None:
        connect_device(selected)

    print("\nProgram finished.")


if __name__ == "__main__":
    main()
