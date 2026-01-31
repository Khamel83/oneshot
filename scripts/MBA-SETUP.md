# MacBook Air Setup Instructions

ONE-SHOT Heartbeat Framework - Manual Setup for MacBook Air

## Prerequisites

- Xcode Command Line Tools: `xcode-select --install`
- Homebrew: `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`
- Node.js: `brew install node`
- Python 3: `brew install python3`
- Age: `brew install age`
- SOPS: `brew install sops`
- Tailscale: https://tailscale.com/download/macos

## Step 1: Clone ONE-SHOT Repo

```bash
mkdir -p ~/github
cd ~/github
git clone github.com/Khamel83/oneshot
cd oneshot
```

## Step 2: Set Up ZAI API Key

Get your API key from: https://z.ai/devpack

Then edit `scripts/claude-shell-setup.sh`:

```bash
# Line ~23, change:
ZAI_API_KEY="YOUR_ZAI_API_KEY_HERE"
# To your actual key:
ZAI_API_KEY="your-actual-api-key-here"
```

## Step 3: Install Claude Code CLI

```bash
npm install -g @anthropic-ai/claude-code
```

## Step 4: Install SOPS/Age Keys

If you have the SOPS/Age key file from another machine:

```bash
# Copy from another machine via Tailscale:
scp macmini@100.113.216.27:~/.age/key.txt ~/.age/key.txt

# Or create new key pair (requires re-encrypting secrets):
age-keygen -o ~/.age/key.txt
```

## Step 5: Run Heartbeat Installer

```bash
cd ~/github/oneshot
bash scripts/claude-shell-setup.sh --install
```

## Step 6: Source Shell Configuration

```bash
# For zsh (default on macOS):
source ~/.zshrc

# Or restart your terminal
```

## Step 7: Test Heartbeat

```bash
# Test manually:
bash ~/github/oneshot/scripts/heartbeat.sh --force

# Test zai command:
zai echo "Hello from z.ai!"
```

## Step 8: Verify Shell Integration

```bash
# Check if heartbeat hook is installed:
grep -e "heartbeat" -e "ONESHOT" ~/.zshrc

# You should see the _oneshot_heartbeat function and PROMPT_COMMAND hook
```

## Usage

### Daily Health Checks

Heartbeat runs automatically when you `cd` into a project with `CLAUDE.md`:

```bash
cd ~/github/oneshot  # Heartbeat runs in background
```

### Manual Heartbeat

```bash
# Force run (bypass date cache):
bash ~/github/oneshot/scripts/heartbeat.sh --force

# Quiet mode:
bash ~/github/oneshot/scripts/heartbeat.sh --quiet

# Background mode:
bash ~/github/oneshot/scripts/heartbeat.sh --background
```

### Available Commands

After setup, you'll have:

- `cc` - Claude Code via Anthropic Pro (YOLO mode)
- `zai` - Claude Code via z.ai GLM API (YOLO mode)
- `oneshot-dismiss "message"` - Dismiss a warning

## Troubleshooting

### ZAI_API_KEY not set

Edit `~/.zshrc` and set your key:

```bash
ZAI_API_KEY="your-actual-api-key-here"
```

Then: `source ~/.zshrc`

### Heartbeat not running automatically

Check if the hook is installed:

```bash
grep "_oneshot_heartbeat" ~/.zshrc
```

If not, re-run:

```bash
cd ~/github/oneshot
bash scripts/claude-shell-setup.sh --install
source ~/.zshrc
```

### Age/SOPS errors

Make sure age is installed:

```bash
age --version
sops --version
```

And the key file exists:

```bash
ls -la ~/.age/key.txt
```

## Next Steps

1. Set up your development projects with `CLAUDE.md` files
2. Heartbeat will run automatically when entering projects
3. Use `zai` for AI assistance via z.ai GLM models
4. Check `~/.claude/state/last-health-check` for last run time

## Support

- ONE-SHOT repo: https://github.com/Khamel83/oneshot
- Claude Code docs: https://docs.anthropic.com/claude-code
- Z.ai docs: https://z.ai/docs
