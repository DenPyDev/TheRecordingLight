# The Recording Light

Shows a red badge when one of the selected microphones is active.

It lists the microphones it can see, lets you tick the ones you want, and keeps the badge on for 10 seconds after the
last sound. On Linux it also checks `pactl`, because `soundcard` alone can miss a mic.

## Run

```bash
bash run.sh
```

That creates `.venv` if needed, installs requirements, and starts the app.

If startup fails:

- Missing `tkinter` on Debian/Ubuntu:

```bash
sudo apt-get install python3-tk
```

## How it behaves

- Only checked microphones are monitored.
- Each checked row shows `idle`, `armed`, `active`, or `error`.
- The numeric level is live.
- The badge lights on very small activity too.
- If nothing else happens for 10 seconds, it hides.

## Notes

- Device names come from the backend.
- If a microphone disappears while the app is running, that row flips to `error`.
