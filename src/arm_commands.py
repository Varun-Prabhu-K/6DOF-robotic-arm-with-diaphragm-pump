
NUM_JOINTS = 6


def format_joint_command(channel: int, angle: int) -> str:
    if not isinstance(channel, int) or isinstance(channel, bool):
        raise ValueError("Channel must be an integer.")
    if not isinstance(angle, int) or isinstance(angle, bool):
        raise ValueError("Angle must be an integer.")
    if not 0 <= channel < NUM_JOINTS:
        raise ValueError("Channel must be between 0 and 5.")
    if not 0 <= angle <= 180:
        raise ValueError("Angle must be between 0 and 180.")

    return f"{channel} ={angle}\n"


def format_action_command(action: str) -> str:
    if action not in ("c", "home", "on", "off"):
        raise ValueError("Unsupported action.")
    return action + "\n"
