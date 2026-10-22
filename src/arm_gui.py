import tkinter as tk
from tkinter import ttk, messagebox
import serial
import serial.tools.list_ports

from arm_commands import format_joint_command, format_action_command


class RoboticArmApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Robotic Arm Control System")
        self.root.geometry("620x650")
        self.connection = None
        self.angles = []

        ttk.Label(
            root, text="6-DOF Robotic Arm Control",
            font=("Arial", 17, "bold")
        ).pack(pady=12)

        connection_frame = ttk.LabelFrame(
            root, text="Arduino Connection", padding=10
        )
        connection_frame.pack(fill="x", padx=15, pady=5)

        self.port = tk.StringVar()
        self.port_box = ttk.Combobox(
            connection_frame, textvariable=self.port, width=18
        )
        self.port_box.pack(side="left", padx=5)

        ttk.Button(
            connection_frame, text="Refresh Ports",
            command=self.refresh_ports
        ).pack(side="left", padx=5)

        self.connect_button = ttk.Button(
            connection_frame, text="Connect",
            command=self.toggle_connection
        )
        self.connect_button.pack(side="left", padx=5)

        self.status = tk.StringVar(value="Disconnected")
        ttk.Label(
            connection_frame, textvariable=self.status
        ).pack(side="left", padx=8)

        joints_frame = ttk.LabelFrame(root, text="Joint Controls", padding=10)
        joints_frame.pack(fill="x", padx=15, pady=8)

        joints_config = [
            ("J0", 1),
            ("J1", 2),
            ("J2", 4),
            ("J3", 0),
            ("J4", 5),
            ("J5", 3)
        ]

        for label, channel in joints_config:
            row = ttk.Frame(joints_frame)
            row.pack(fill="x", pady=4)

            ttk.Label(row, text=f"{label} (CH {channel})", width=12).pack(
                side="left"
            )

            angle = tk.IntVar(value=90)
            self.angles.append(angle)

            ttk.Scale(
                row, from_=0, to=180, variable=angle,
                orient="horizontal"
            ).pack(side="left", fill="x", expand=True, padx=8)

            ttk.Label(row, textvariable=angle, width=4).pack(side="left")

            ttk.Button(
                row, text="Move",
                command=lambda ch=channel, a=angle: self.move_joint(ch, a)
            ).pack(side="left", padx=5)

        action_frame = ttk.LabelFrame(root, text="Actions", padding=10)
        action_frame.pack(fill="x", padx=15, pady=8)

        ttk.Button(
            action_frame, text="Center All",
            command=lambda: self.send_action("c")
        ).pack(side="left", padx=8)

        ttk.Button(
            action_frame, text="Pump ON",
            command=lambda: self.send_action("on")
        ).pack(side="left", padx=8)

        ttk.Button(
            action_frame, text="Pump OFF",
            command=lambda: self.send_action("off")
        ).pack(side="left", padx=8)

        log_frame = ttk.LabelFrame(root, text="Communication Log", padding=8)
        log_frame.pack(fill="both", expand=True, padx=15, pady=8)

        self.log = tk.Text(log_frame, height=8, state="disabled")
        self.log.pack(fill="both", expand=True)

        self.refresh_ports()
        self.root.after(200, self.read_responses)
        self.root.protocol("WM_DELETE_WINDOW", self.close_app)

    def write_log(self, message):
        self.log.configure(state="normal")
        self.log.insert("end", message + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def refresh_ports(self):
        ports = [p.device for p in serial.tools.list_ports.comports()]
        self.port_box["values"] = ports
        if ports and self.port.get() not in ports:
            self.port.set(ports[0])
        self.write_log("Available ports: " + (", ".join(ports) or "None"))

    def toggle_connection(self):
        if self.connection and self.connection.is_open:
            self.connection.close()
            self.connection = None
            self.connect_button.configure(text="Connect")
            self.status.set("Disconnected")
            self.write_log("Disconnected from Arduino.")
            return

        selected = self.port.get().strip()
        if not selected:
            messagebox.showwarning("No port", "Select an Arduino COM port.")
            return

        try:
            self.connection = serial.Serial(
                selected, 9600, timeout=0.1, write_timeout=1
            )
            self.connect_button.configure(text="Disconnect")
            self.status.set("Connected: " + selected)
            self.write_log("Connected to " + selected)
            self.write_log("Allow the Arduino to finish restarting.")
        except (serial.SerialException, OSError) as exc:
            self.connection = None
            messagebox.showerror("Connection failed", str(exc))

    def send_command(self, command):
        if not self.connection or not self.connection.is_open:
            messagebox.showwarning("Not connected", "Connect to the Arduino first.")
            return

        try:
            self.connection.write(command.encode("ascii"))
            self.write_log("Sent: " + repr(command.strip()))
        except (serial.SerialException, OSError) as exc:
            self.status.set("Communication error")
            self.write_log("ERROR: " + str(exc))

    def move_joint(self, channel, angle):
        try:
            command = format_joint_command(channel, angle.get())
            self.send_command(command)
        except ValueError as exc:
            messagebox.showerror("Invalid command", str(exc))

    def send_action(self, action):
        if action == "on":
            if not messagebox.askyesno(
                "Activate pump", "Turn the suction pump ON?"
            ):
                return

        self.send_command(format_action_command(action))

    def read_responses(self):
        if self.connection and self.connection.is_open:
            try:
                while self.connection.in_waiting:
                    response = self.connection.readline().decode(
                        "utf-8", errors="replace"
                    ).strip()
                    if response:
                        self.write_log("Arduino: " + response)
            except (serial.SerialException, OSError) as exc:
                self.write_log("Read error: " + str(exc))
                self.status.set("Communication error")

        self.root.after(200, self.read_responses)

    def close_app(self):
        if self.connection and self.connection.is_open:
            self.connection.close()
        self.root.destroy()


if __name__ == "__main__":
    window = tk.Tk()
    app = RoboticArmApp(window)
    window.mainloop()
