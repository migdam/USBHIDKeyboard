"""
OTA (Over-The-Air) Firmware Updater for PMIA
Allows uploading .uf2 files via Web UI for firmware updates
"""
import storage
import microcontroller
import os


class OTAUpdater:
    """
    Handles OTA firmware updates

    Note: This is a simplified implementation.
    Actual OTA on Pico requires entering bootloader mode,
    which typically requires a physical button press or power cycle.
    """

    UPLOAD_DIR = "/uploads"
    MAX_UPLOAD_SIZE = 2 * 1024 * 1024  # 2 MB

    def __init__(self, settings):
        """
        Initialize OTA updater

        Args:
            settings: Settings instance
        """
        self.settings = settings
        self.enabled = settings.get("enable_ota", True)

        # Ensure upload directory exists
        self._ensure_upload_dir()

    def _ensure_upload_dir(self):
        """Create upload directory if needed"""
        try:
            if self.UPLOAD_DIR.strip("/") not in os.listdir("/"):
                os.mkdir(self.UPLOAD_DIR)
        except Exception as e:
            print(f"Upload dir creation failed: {e}")

    def verify_uf2(self, file_path):
        """
        Verify UF2 file format

        Args:
            file_path: Path to .uf2 file

        Returns:
            bool: True if valid UF2
        """
        try:
            with open(file_path, "rb") as f:
                # Read UF2 magic number
                magic = f.read(4)
                # UF2 magic: 0x0A324655
                return magic == b'\x55\x46\x32\x0A' or magic == b'\x0A\x46\x32\x55'
        except:
            return False

    def save_upload(self, filename, data):
        """
        Save uploaded firmware file

        Args:
            filename: Name of file
            data: File data (bytes)

        Returns:
            str: Path to saved file or None on error
        """
        if not self.enabled:
            print("OTA disabled")
            return None

        if len(data) > self.MAX_UPLOAD_SIZE:
            print(f"Upload too large: {len(data)} bytes")
            return None

        if not filename.endswith('.uf2'):
            print("Invalid file extension")
            return None

        try:
            # Remount as writable
            storage.remount("/", False)

            path = f"{self.UPLOAD_DIR}/{filename}"

            with open(path, "wb") as f:
                f.write(data)

            # Remount as read-only
            storage.remount("/", True)

            # Verify file
            if not self.verify_uf2(path):
                print("Invalid UF2 file")
                os.remove(path)
                return None

            print(f"Firmware saved: {path}")
            return path

        except Exception as e:
            print(f"Upload save failed: {e}")
            return None

    def apply_update(self, file_path):
        """
        Apply firmware update

        Note: On Raspberry Pi Pico, this requires:
        1. Copying firmware to /boot partition (not accessible from CircuitPython)
        2. Entering bootloader mode (BOOTSEL button)

        This is a placeholder for documentation purposes.
        Actual implementation requires custom bootloader or manual process.

        Args:
            file_path: Path to .uf2 file

        Returns:
            bool: Success status
        """
        if not self.verify_uf2(file_path):
            print("Invalid firmware file")
            return False

        print("=" * 50)
        print("FIRMWARE UPDATE INSTRUCTIONS")
        print("=" * 50)
        print("1. Download the firmware file to your computer")
        print("2. Disconnect the Pico from USB")
        print("3. Hold BOOTSEL button and reconnect USB")
        print("4. Pico will appear as a USB drive")
        print("5. Copy the .uf2 file to the drive")
        print("6. Pico will reboot with new firmware")
        print("=" * 50)

        return True

    def reboot(self):
        """Reboot the device"""
        print("Rebooting...")
        microcontroller.reset()

    def enter_bootloader(self):
        """
        Enter bootloader mode

        Note: This may not work on all CircuitPython versions
        """
        try:
            print("Entering bootloader mode...")
            microcontroller.on_next_reset(microcontroller.RunMode.BOOTLOADER)
            microcontroller.reset()
        except Exception as e:
            print(f"Bootloader entry failed: {e}")
            print("Please manually enter bootloader (BOOTSEL button)")


# Global OTA updater
ota_updater = None

def init_ota_updater(settings):
    """Initialize global OTA updater"""
    global ota_updater
    ota_updater = OTAUpdater(settings)
    return ota_updater
