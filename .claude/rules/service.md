# Service/API Rules (Python + systemd)

## Default Stack

When building services/APIs for this user:

```
Python + systemd → Deploy to oci-dev
```

## When to Use

Detect by presence of:
- `*.service` systemd file
- `main.py` or `app.py` with long-running process
- No web framework files

## Deployment Target

- **oci-dev** (100.126.13.70) - Default service deployment
- **systemd user service** - For persistent processes
- **Tailscale networking** - All machines on deer-panga.ts.net

## Service Pattern

```python
# Standard service structure
import signal
import sys

class Service:
    def __init__(self):
        self.running = True

    def run(self):
        signal.signal(signal.SIGTERM, self.shutdown)
        # Main loop here

    def shutdown(self, signum, frame):
        self.running = False
```

## systemd Integration

- **User services** - `~/.config/systemd/user/`
- **Auto-restart** - `Restart=on-failure`
- **Logging** - `StandardOutput=journal`

## Storage

- **SQLite (default)** - For service data
- **homelab (26TB)** - For large storage needs
- **Tailscale** - For network communication

## Anti-Patterns

- ❌ Don't suggest Docker for deployment
- ❌ Don't suggest cloud providers (AWS, GCP, Azure)
- ❌ Don't suggest nginx/traefik (use Tailscale Funnel + poytz)
