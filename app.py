import time
from flask import Flask, render_template, request, jsonify
import serial
import serial.tools.list_ports
from src.arm_commands import format_joint_command, format_action_command

app = Flask(__name__)

arduino = None
current_port = None


@app.after_request
def add_cache_headers(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/ports")
def get_ports():
    ports = []
    for p in serial.tools.list_ports.comports():
        ports.append({
            "device": p.device,
            "description": p.description or p.device
        })
    return jsonify(ports)


@app.route("/api/status")
def get_status():
    global arduino, current_port
    is_connected = bool(arduino and arduino.is_open)
    return jsonify({
        "connected": is_connected,
        "port": current_port if is_connected else None
    })


@app.route("/api/connect", methods=["POST"])
def connect():
    global arduino, current_port
    data = request.get_json(silent=True) or {}
    port = data.get("port", "").strip()

    if not port:
        return jsonify({"ok": False, "message": "No COM port specified"}), 400

    try:
        if arduino and arduino.is_open:
            try:
                arduino.close()
            except Exception:
                pass
            arduino = None
            current_port = None

        # Open serial port with 9600 baud rate matching Arduino firmware
        arduino = serial.Serial(
            port=port,
            baudrate=9600,
            timeout=0.1,
            write_timeout=1.0
        )
        current_port = port

        # Small pause for Arduino UNO to stabilize after serial reset (DTR toggle)
        time.sleep(1.8)
        arduino.reset_input_buffer()

        return jsonify({
            "ok": True,
            "message": f"Connected successfully to {port}."
        })

    except (serial.SerialException, OSError, ValueError) as exc:
        if arduino and arduino.is_open:
            try:
                arduino.close()
            except Exception:
                pass
        arduino = None
        current_port = None
        return jsonify({"ok": False, "message": str(exc)}), 400


@app.route("/api/disconnect", methods=["POST"])
def disconnect():
    global arduino, current_port
    try:
        if arduino and arduino.is_open:
            arduino.close()
    except Exception:
        pass
    arduino = None
    current_port = None
    return jsonify({"ok": True, "message": "Disconnected successfully."})


@app.route("/api/command", methods=["POST"])
def command():
    global arduino
    data = request.get_json(silent=True) or {}
    kind = data.get("kind")

    if not arduino or not arduino.is_open:
        return jsonify({"ok": False, "message": "Arduino is not connected. Please connect first."}), 400

    try:
        if kind == "joint":
            channel = int(data.get("channel"))
            angle = int(data.get("angle"))
            cmd = format_joint_command(channel, angle)
        elif kind == "action":
            action = str(data.get("action"))
            cmd = format_action_command(action)
        elif kind == "raw":
            raw_text = str(data.get("command", "")).strip()
            if not raw_text:
                return jsonify({"ok": False, "message": "Empty raw command"}), 400
            cmd = raw_text + "\n"
        else:
            return jsonify({"ok": False, "message": f"Unknown command type: {kind}"}), 400

        arduino.write(cmd.encode("ascii"))
        arduino.flush()
        return jsonify({"ok": True, "sent": cmd.strip()})

    except (ValueError, TypeError) as exc:
        return jsonify({"ok": False, "message": str(exc)}), 400
    except (serial.SerialException, OSError) as exc:
        arduino = None
        return jsonify({"ok": False, "message": f"Serial communication error: {exc}"}), 500


@app.route("/api/response")
def response():
    global arduino
    if not arduino or not arduino.is_open:
        return jsonify({"connected": False, "lines": []})

    lines = []
    try:
        while arduino.in_waiting > 0:
            raw_line = arduino.readline()
            if not raw_line:
                break
            line_str = raw_line.decode("utf-8", errors="replace").strip()
            if line_str:
                lines.append(line_str)
        return jsonify({"connected": True, "lines": lines})
    except (serial.SerialException, OSError) as exc:
        arduino = None
        return jsonify({"connected": False, "lines": [f"Connection error: {exc}"]}), 500


if __name__ == "__main__":
    print("Starting 6-DOF Robotic Arm Control Server on http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=False)
