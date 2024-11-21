import tkinter as tk

from views.components.section_frame import SectionFrame
from views.themes import UI_COLORS, UI_FONTS


class StatusSection:
    def __init__(self, parent, bot_ui):
        self.bot_ui = bot_ui
        self.section = SectionFrame(parent, "Status")
        self.section.frame.pack(fill=tk.X, pady=5)
        self.setup_status()

    def setup_status(self):
        status_container = tk.Frame(self.section.frame, bg=UI_COLORS["bg"])
        status_container.pack(fill=tk.X, pady=5)

        self.status_label = tk.Label(
            status_container,
            text="Status: Not running",
            font=UI_FONTS["text"],
            fg=UI_COLORS["error"],
            bg=UI_COLORS["bg"],
        )
        self.status_label.pack(side=tk.LEFT, pady=5)

        debug_button = tk.Button(
            status_container,
            text="🔍 Debug",
            command=self.bot_ui.ui_actions.toggle_debug_window,
            font=UI_FONTS["text"],
            relief=tk.FLAT,
            bg=UI_COLORS["button_bg"],
            fg=UI_COLORS["fg"],
            padx=10,
        )
        debug_button.pack(side=tk.RIGHT, padx=5)

        self.selected_emulator_label = tk.Label(
            self.section.frame,
            text="",
            font=UI_FONTS["text"],
            bg=UI_COLORS["entry_bg"],
            fg=UI_COLORS["entry_fg"],
            relief=tk.FLAT,
            padx=5,
        )
        self.selected_emulator_label.pack(fill=tk.X, padx=5, pady=2)

        # Add connection status indicator
        self.connection_label = tk.Label(
            self.section.frame,
            text="📱 Not Connected",
            font=UI_FONTS["text"],
            bg=UI_COLORS["bg"],
            fg=UI_COLORS["error"],
        )
        self.connection_label.pack(fill=tk.X, pady=2)

        # Start periodic connection check
        self.check_connection_status()

    def update_emulator_path(self, path):
        self.selected_emulator_label.config(text=path)

    def check_connection_status(self):
        devices = self.bot_ui.bot.emulator_controller.get_all_devices()
        connected_device = next(
            (
                d
                for d in devices
                if d["state"] == "device"
                and d["id"] == self.bot_ui.app_state.emulator_name
            ),
            None,
        )

        if connected_device:
            self.connection_label.config(
                text=f"📱 Connected to: {connected_device['id']}",
                fg=UI_COLORS["success"],
            )
        else:
            self.connection_label.config(text="📱 Not Connected", fg=UI_COLORS["error"])

        # Schedule next check
        self.section.frame.after(2000, self.check_connection_status)
