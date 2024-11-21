import time
import tkinter as tk
import traceback

from views.themes import UI_COLORS, UI_FONTS


class DeviceConnectionDialog:
    def __init__(self, parent, emulator_controller, app_state, log_callback):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Connect to Device")
        self.dialog.geometry("500x400")
        self.dialog.configure(bg=UI_COLORS["bg"])

        self.emulator_controller = emulator_controller
        self.app_state = app_state
        self.log_callback = log_callback

        # Add status label
        self.status_label = tk.Label(
            self.dialog,
            text="",
            font=UI_FONTS["text"],
            bg=UI_COLORS["bg"],
            fg=UI_COLORS["fg"],
            wraplength=450,
        )
        self.status_label.pack(pady=5)

        self.setup_ui()
        self.refresh_devices()

    def update_status(self, message, is_error=False):
        self.status_label.config(
            text=message, fg=UI_COLORS["error"] if is_error else UI_COLORS["success"]
        )
        self.log_callback(message)

    def setup_ui(self):
        # Title
        tk.Label(
            self.dialog,
            text="Available Devices",
            font=UI_FONTS["header"],
            bg=UI_COLORS["bg"],
            fg=UI_COLORS["accent"],
        ).pack(pady=10)

        # Device list
        self.device_frame = tk.Frame(self.dialog, bg=UI_COLORS["bg"])
        self.device_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Buttons frame
        button_frame = tk.Frame(self.dialog, bg=UI_COLORS["bg"])
        button_frame.pack(fill=tk.X, padx=20, pady=10)

        # Refresh button
        tk.Button(
            button_frame,
            text="🔄 Refresh",
            command=self.refresh_devices,
            bg=UI_COLORS["button_bg"],
            fg=UI_COLORS["fg"],
            font=UI_FONTS["text"],
            relief=tk.FLAT,
        ).pack(side=tk.LEFT, padx=5)

        # Close button
        tk.Button(
            button_frame,
            text="Close",
            command=self.dialog.destroy,
            bg=UI_COLORS["button_bg"],
            fg=UI_COLORS["fg"],
            font=UI_FONTS["text"],
            relief=tk.FLAT,
        ).pack(side=tk.RIGHT, padx=5)

    def refresh_devices(self):
        # Clear existing devices
        for widget in self.device_frame.winfo_children():
            widget.destroy()

        # Get devices
        devices = self.emulator_controller.get_all_devices()

        if not devices:
            tk.Label(
                self.device_frame,
                text="No devices found",
                font=UI_FONTS["text"],
                bg=UI_COLORS["bg"],
                fg=UI_COLORS["fg"],
            ).pack(pady=10)
            return

        # Create device buttons
        for device in devices:
            device_frame = tk.Frame(self.device_frame, bg=UI_COLORS["bg"])
            device_frame.pack(fill=tk.X, pady=2)

            # Format device ID for display
            display_id = device["id"]
            if ":" not in display_id and display_id.isdigit():
                display_id = f"127.0.0.1:{display_id}"

            # Device info
            is_connected = (
                device["id"] == self.app_state.emulator_name
                and device["state"] == "device"
            )
            status_color = (
                UI_COLORS["success"]
                if device["state"] == "device"
                else UI_COLORS["error"]
            )

            tk.Label(
                device_frame,
                text=f"• {display_id}",
                font=UI_FONTS["text"],
                bg=UI_COLORS["bg"],
                fg=status_color,
            ).pack(side=tk.LEFT, padx=5)

            # Connect/Switch button
            button_text = "Connected" if is_connected else "Connect"
            button_state = "disabled" if is_connected else "normal"

            tk.Button(
                device_frame,
                text=button_text,
                command=lambda d=device: self.switch_device(d),
                state=button_state,
                bg=UI_COLORS["button_bg"],
                fg=UI_COLORS["fg"],
                font=UI_FONTS["text"],
                relief=tk.FLAT,
            ).pack(side=tk.RIGHT, padx=5)

        # Force update the dialog
        self.dialog.update_idletasks()

    def switch_device(self, new_device):
        try:
            self.update_status(f"Attempting to connect to {new_device['id']}...")
            self.dialog.update()

            # If there's a currently connected device, disconnect it first
            if self.app_state.emulator_name:
                self.update_status(
                    f"Disconnecting current device: {self.app_state.emulator_name}"
                )
                self.emulator_controller.disconnect_all_devices()
                time.sleep(1)

            # Try to connect using connect_and_run first
            if self.emulator_controller.connect_and_run():
                # Update app state with the new device
                self.app_state.emulator_name = new_device["id"]
                self.update_status(f"✅ Successfully connected to {new_device['id']}")
                self.refresh_devices()  # This will update the UI
                return

            # If connect_and_run fails, try direct connection
            connection_result = self.emulator_controller.connect_to_device(
                new_device["id"]
            )

            if connection_result:
                self.app_state.emulator_name = new_device["id"]
                self.update_status(f"✅ Successfully connected to {new_device['id']}")
                self.refresh_devices()  # This will update the UI
            else:
                error_msg = f"❌ Failed to connect to {new_device['id']}\nCheck terminal for detailed error logs"
                self.update_status(error_msg, is_error=True)
                self.refresh_devices()  # Refresh UI even on failure

        except Exception as e:
            error_msg = (
                f"❌ Connection error: {e!s}\nCheck terminal for detailed error logs"
            )
            self.update_status(error_msg, is_error=True)
            print("\n=== Dialog Error ===")
            print(f"Error type: {type(e).__name__}")
            print(f"Error message: {e!s}")
            print(traceback.format_exc())
            self.refresh_devices()  # Refresh UI even on error
