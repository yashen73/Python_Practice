
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
    """Scan nearby devices and collect names as they are discovered."""
    import selectors

    print("\nScanning for Bluetooth devices...")
    print("Waiting 15 seconds for device names...\n")

    devices = {}
    process = None

    try:
        process = subprocess.Popen(
            ["bluetoothctl"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        selector = selectors.DefaultSelector()
        selector.register(process.stdout, selectors.EVENT_READ)

        def send_command(command):
            process.stdin.write(command + "\n")
            process.stdin.flush()

        send_command("power on")
        send_command("agent on")
        send_command("default-agent")
        send_command("scan on")

        start = time.monotonic()

        while time.monotonic() - start < 15:
            events = selector.select(timeout=0.5)

            for key, _ in events:
                line = key.fileobj.readline().strip()

                # Example: [NEW] Device AA:BB:CC:DD:EE:FF My Phone
                match = re.search(
                    r"(?:\[NEW\]\s+)?Device\s+"
                    r"([0-9A-Fa-f:]{17})\s+(.+)",
                    line
                )

                if match:
                    mac = match.group(1).upper()
                    name = match.group(2).strip()

                    if name and name.lower() not in (
                        "unknown", "n/a"
                    ):
                        devices[mac] = name

                # Example: [CHG] Device AA:BB:CC:DD:EE:FF Name: My Phone
                match = re.search(
                    r"Device\s+([0-9A-Fa-f:]{17})\s+"
                    r"(?:Name|Alias):\s*(.+)",
                    line
                )

                if match:
                    mac = match.group(1).upper()
                    name = match.group(2).strip()

                    if name:
                        devices[mac] = name

        send_command("scan off")
        time.sleep(1)

        # Ask BlueZ for all known devices as a fallback.
        send_command("devices")
        time.sleep(1)

        while selector.select(timeout=0.2):
            line = process.stdout.readline().strip()

            match = re.search(
                r"Device\s+([0-9A-Fa-f:]{17})\s+(.+)",
                line
            )

            if match:
                mac = match.group(1).upper()
                name = match.group(2).strip()

                if name:
                    devices.setdefault(mac, name)

        # Query each device for its full name or alias.
        for mac in list(devices.keys()):
            info = run_command(
                ["bluetoothctl", "info", mac],
                timeout=5
            )

            name_match = re.search(
                r"^\s*(?:Name|Alias):\s*(.+)$",
                info,
                re.MULTILINE
            )

            if name_match:
                devices[mac] = name_match.group(1).strip()

        selector.close()

    except Exception as e:
        print(f"Bluetooth scan error: {e}")

    finally:
        if process is not None:
            try:
                process.terminate()
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()

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
