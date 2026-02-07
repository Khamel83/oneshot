# RelayQ: GitHub-First Hybrid Runner Kit

A job orchestration platform that uses GitHub's native queue system with self-hosted runners for local processing. Zero inbound ports required, free for personal use.

## Architecture

```
OCI VM  ───▶  GitHub (queue)  ◀── polling ──  Mac mini / RPi4 / RPi3
   │             ▲  ▲                                │
   └─ gh/api ────┘  └── logs/secrets                 └─(optional) Tailscale to private data
```

## What This Is

**GitHub-first job orchestration** - Use GitHub Actions as your job queue and self-hosted runners for processing. No Redis, no inbound ports, no maintenance overhead.

**Perfect for:**
- Audio/video processing
- File transcoding
- Data processing workflows
- Background task automation
- Personal compute orchestration

## Quick Start

### 1. Install Runners

**Mac mini (heavy processing):**
```bash
# See docs/SETUP_RUNNERS_mac.md
curl -O -L https://github.com/actions/runner/releases/download/v2.311.0/actions-runner-osx-x64-2.311.0.tar.gz
tar xzf actions-runner-osx-x64-2.311.0.tar.gz
sudo ./config.sh --url https://github.com/Khamel83/relayq --token YOUR_TOKEN
sudo ./svc.sh install && sudo ./svc.sh start
```

**Raspberry Pi 4 (light processing):**
```bash
# See docs/SETUP_RUNNERS_rpi.md
sudo useradd -m runner
sudo -u runner bash -c 'cd /opt/actions-runner && ./config.sh --url https://github.com/Khamel83/relayq --token YOUR_TOKEN'
```

### 2. Configure OCI VM Trigger

```bash
# Install GitHub CLI
sudo apt install gh
gh auth login

# Test job submission
./bin/dispatch.sh .github/workflows/transcribe_audio.yml url=https://example.com/audio.mp3
```

### 3. Submit Jobs

**From OCI VM:**
```bash
# Pooled execution (Mac mini or RPi4)
./bin/dispatch.sh .github/workflows/transcribe_audio.yml url=https://example.com/episode.mp3

# Force Mac mini execution
./bin/dispatch.sh .github/workflows/transcribe_mac.yml url=https://example.com/large.mp3

# Force RPi4 execution
./bin/dispatch.sh .github/workflows/transcribe_rpi.yml url=https://example.com/small.mp3
```

**From GitHub UI:**
1. Go to Actions tab
2. Select workflow
3. Click "Run workflow"
4. Enter URL and parameters

## Runner Labels

| Runner | Labels | Use Case |
|--------|--------|----------|
| **Mac mini** | `self-hosted, macmini, audio, ffmpeg, heavy` | Video/audio transcoding, heavy processing |
| **RPi4** | `self-hosted, rpi4, audio, light` | Text processing, small audio files |
| **RPi3** | `self-hosted, rpi3, overflow, verylight` | Background tasks, overflow |

## Workflows

- **`transcribe_audio.yml`** - Pooled execution across available runners
- **`transcribe_mac.yml`** - Mac mini only (heavy tasks)
- **`transcribe_rpi.yml`** - RPi4 only (light tasks)

## Backends

### Local Whisper
- **Cost**: Free (electricity only)
- **Privacy**: Complete
- **Performance**: Good (depends on hardware)
- **Setup**: Install whisper/whisper.cpp

### OpenAI API
- **Cost**: ~$0.006/minute
- **Privacy**: None
- **Performance**: Excellent
- **Setup**: API key required

### Router APIs (OpenRouter)
- **Cost**: Variable
- **Privacy**: Limited
- **Performance**: Excellent
- **Setup**: API key required

## Configuration

### Runner Environment
```bash
# Create ~/.config/relayq/env
mkdir -p ~/.config/relayq
cat > ~/.config/relayq/env << 'EOF'
ASR_BACKEND=local
WHISPER_MODEL=base

# Just paste your API key here - works with OpenAI, OpenRouter, etc.
AI_API_KEY=sk-your-api-key-here
EOF
```

### Job Routing Policy
```yaml
# policy/policy.yaml
routes:
  transcribe:
    prefer: [macmini]
    fallback: [rpi4]
    constraints:
      needs_ffmpeg: true
      max_size_mb: 1000
```

## Documentation

- **[docs/OVERVIEW.md](docs/OVERVIEW.md)** - Architecture and motivation
- **[docs/SETUP_RUNNERS_mac.md](docs/SETUP_RUNNERS_mac.md)** - macOS runner setup
- **[docs/SETUP_RUNNERS_rpi.md](docs/SETUP_RUNNERS_rpi.md)** - Raspberry Pi setup
- **[docs/SETUP_OCI_TRIGGER.md](docs/SETUP_OCI_TRIGGER.md)** - OCI VM trigger setup
- **[docs/RUNBOOK.md](docs/RUNBOOK.md)** - Operations procedures
- **[docs/RELIABILITY.md](docs/RELIABILITY.md)** - Reliability patterns
- **[docs/ROUTING_POLICY.md](docs/ROUTING_POLICY.md)** - Policy engine
- **[docs/LLM_ROUTING.md](docs/LLM_ROUTING.md)** - Backend routing
- **[docs/OPSEC.md](docs/OPSEC.md)** - Security practices
- **[docs/DECISIONS.md](docs/DECISIONS.md)** - Migration decisions
- **[docs/TASKS.md](docs/TASKS.md)** - Implementation checklist

## Examples

### Audio Transcription
```bash
# Basic transcription
./bin/dispatch.sh .github/workflows/transcribe_audio.yml \
  url=https://example.com/podcast.mp3

# With specific backend
./bin/dispatch.sh .github/workflows/transcribe_audio.yml \
  url=https://example.com/interview.mp3 \
  backend=openai

# Large file on Mac mini
./bin/dispatch.sh .github/workflows/transcribe_mac.yml \
  url=https://example.com/lecture.mp3 \
  backend=local \
  model=small
```

### API Integration
```python
import subprocess

def submit_transcription(audio_url, backend="local"):
    """Submit transcription job from external application"""
    cmd = [
        '/home/ubuntu/relayq/bin/dispatch.sh',
        '.github/workflows/transcribe_audio.yml',
        f'url={audio_url}',
        f'backend={backend}'
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Job submission failed: {result.stderr}")

    return result.stdout.strip()

# Usage
result = submit_transcription(
    "https://example.com/episode.mp3",
    backend="local"
)
print(f"Job submitted: {result}")
```

## Migration from Redis

The original Redis-based implementation is preserved in `legacy/`. See `legacy/ARCHIVE.md` for re-enabling instructions.

## Security

- **Outbound-only connections** - No inbound ports required
- **Secret management** - GitHub encrypted secrets + node-local env files
- **Isolated execution** - Jobs run in isolated environments
- **No data exposure** - Everything processes locally

## Troubleshooting

### Jobs Stay Queued
1. Check runner status: `gh api repos/Khamel83/relayq/actions/runners`
2. Verify labels match workflow requirements
3. Restart runner service if needed

### Jobs Fail
1. Check workflow logs in GitHub UI
2. Verify dependencies installed on runner
3. Check environment variables and API keys

### Runner Offline
1. Check network connectivity: `ping github.com`
2. Restart runner service
3. Re-register runner if needed

## Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

## License

Original project license preserved. See LICENSE file for details.

## Support

- **Documentation**: See `docs/` directory
- **Issues**: Open GitHub issue
- **Community**: Discussions tab

---

**Cost**: Free (GitHub Actions 2,000 minutes/month + local hardware)
**Maintenance**: Minimal (auto-restart runners)
**Security**: High (outbound-only, isolated execution)
**Scalability**: Good for personal/small business use