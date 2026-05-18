import re
import subprocess
from dataclasses import dataclass

try:
    import numpy as np
except Exception:
    np = None

try:
    import soundcard as sc

    SC_ERROR = None
except Exception as exc:
    sc = None
    SC_ERROR = exc

RATE = 48000
BLOCK = 1024
INPUT_PORT_WORDS = (
    "mic",
    "microphone",
    "input",
    "handsfree",
    "headset",
    "digital input",
    "spdif",
)


@dataclass(frozen=True)
class Device:
    key: str
    name: str
    ids: tuple[str, ...]


def startup_errors():
    errors = []
    if np is None:
        errors.append("No `numpy` in the venv. Run `bash run.sh`.")
    if sc is None:
        detail = str(SC_ERROR).strip() or "load error"
        errors.append(
            f"No `soundcard`: {detail}. Run `bash run.sh`. "
            "On Linux you may also need `libpulse`."
        )
    return errors


def normalize(text):
    return re.sub(r"\s+", " ", str(text or "").strip()).lower()


def compact_ids(*values):
    result = []
    for value in values:
        value = str(value or "").strip()
        if value and value not in result:
            result.append(value)
    return tuple(result)


def soundcard_call(name, *args, **kwargs):
    func = getattr(sc, name)
    try:
        return func(*args, **kwargs)
    except TypeError:
        kwargs.pop("include_loopback", None)
        return func(*args, **kwargs)


def run_pactl(*args):
    try:
        return subprocess.check_output(
            ["pactl", *args],
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        return ""


def match_one(text, pattern):
    match = re.search(pattern, text, re.M)
    return match.group(1).strip() if match else ""


def parse_sources(text):
    devices = []
    for block in re.split(r"(?m)(?=^Source #\d+)", text):
        if 'media.class = "Audio/Source"' not in block:
            continue
        name = match_one(block, r"^\s*Name:\s*(.+)$")
        if not name:
            continue
        desc = match_one(block, r"^\s*Description:\s*(.+)$")
        nick = match_one(block, r'^\s*node\.nick = "([^"]+)"')
        card = match_one(block, r'^\s*device\.description = "([^"]+)"')
        label = f"{nick} {card}".strip() if nick and card else desc or nick or name
        devices.append(Device(f"source:{name}", label, compact_ids(name, desc, nick, card)))
    return devices


def parse_cards(text):
    devices = []
    for block in re.split(r"(?m)(?=^Card #\d+)", text):
        card = match_one(block, r'^\s*device\.description = "([^"]+)"')
        card = card or match_one(block, r"^\s*Name:\s*(.+)$") or "Input Device"
        ports = re.findall(r"^\s+(\S+):\s+(.+?)\s+\(type:", block, re.M)
        for port_name, port_desc in ports:
            blob = normalize(f"{port_name} {port_desc}")
            if not any(word in blob for word in INPUT_PORT_WORDS):
                continue
            label = f"{port_desc} {card}"
            devices.append(Device(f"card:{card}:{port_name}", label, compact_ids(label, card, port_desc, port_name)))
    return devices


def discover_devices():
    devices = []
    seen_keys = set()
    seen_marks = set()

    def add(device):
        marks = {normalize(device.name), *(normalize(item) for item in device.ids)}
        if device.key in seen_keys or any(mark in seen_marks for mark in marks):
            return
        seen_keys.add(device.key)
        seen_marks.update(marks)
        devices.append(device)

    if sc is not None:
        try:
            found = [soundcard_call("default_microphone")]
            found += list(soundcard_call("all_microphones", include_loopback=False) or [])
            for mic in found:
                if mic is None:
                    continue
                mic_id = str(getattr(mic, "id", "") or "").strip()
                name = str(getattr(mic, "name", "") or "").strip() or mic_id or "Microphone"
                add(Device(f"sc:{mic_id or name}", name, compact_ids(mic_id, name)))
        except Exception:
            pass

    for device in parse_sources(run_pactl("list", "sources")):
        add(device)
    for device in parse_cards(run_pactl("list", "cards")):
        add(device)

    devices.sort(key=lambda item: normalize(item.name))
    return devices


def resolve_microphone(device):
    if sc is None:
        return None

    for candidate in device.ids:
        try:
            return soundcard_call("get_microphone", candidate, include_loopback=False)
        except Exception:
            pass

    try:
        for mic in soundcard_call("all_microphones", include_loopback=False) or []:
            blob = " ".join(normalize(getattr(mic, part, "")) for part in ("id", "name"))
            if any(normalize(candidate) and normalize(candidate) in blob for candidate in device.ids):
                return mic
    except Exception:
        pass

    return None


def open_recorder(mic):
    attempts = (
        {"samplerate": RATE, "channels": None, "blocksize": BLOCK},
        {"samplerate": RATE, "channels": 1, "blocksize": BLOCK},
        {"samplerate": RATE, "blocksize": BLOCK},
        {},
    )
    for kwargs in attempts:
        try:
            return mic.recorder(**kwargs)
        except Exception:
            pass
    raise RuntimeError("Could not open microphone")


def level_value(data):
    if np is None or getattr(data, "size", 0) == 0:
        return 0.0
    return float(np.sqrt(np.mean(np.square(data))))
