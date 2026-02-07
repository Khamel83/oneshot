# /remote — Execute on Remote Machines via SSH

Execute commands across the Tailscale network (brain/body/muscle architecture).

## Machine Registry

| Machine | SSH Alias | User | Purpose |
|---------|-----------|------|---------|
| oci-dev | `oci-dev` | ubuntu | Claude Code, APIs, OCI resources |
| homelab | `homelab` | khamel83 | Docker (53+ services), 26TB storage |
| macmini | `macmini` | macmini | Apple Silicon GPU, transcription |

## Workflow A: Sync and Run

Push code via git, pull on target, execute.

```bash
TARGET="homelab"  # or macmini, oci-dev
REPO="my-project"
BRANCH="main"
COMMAND="python scripts/process.py"

# Push local changes
git push origin "$BRANCH"

# Pull and execute on remote
ssh $TARGET << REMOTE
  set -e
  cd ~/github/$REPO
  [ -n "\$(git status --porcelain)" ] && git stash push -m "remote-exec auto-stash"
  git pull --ff-only origin $BRANCH
  $COMMAND
REMOTE
```

## Workflow B: Data Transfer (Process on Remote)

```bash
# Transfer files to macmini for GPU processing
rsync -avz --progress homelab:/mnt/main-drive/videos/raw/ macmini:~/data/processing/

# Process on macmini
ssh macmini "cd ~/data/processing && python ~/github/atlas/scripts/transcribe.py"

# Transfer results back
rsync -avz --progress macmini:~/data/processing/output/ homelab:/mnt/main-drive/videos/transcribed/
```

## Workflow C: Long-Running Job (tmux)

```bash
TARGET="homelab"
JOB_NAME="index-rebuild"
COMMAND="python scripts/full_index.py"
WORKING_DIR="~/github/atlas"
SESSION="remote-exec-${TARGET}-$(date +%Y%m%d-%H%M)-${JOB_NAME}"

# Start in tmux
ssh $TARGET "tmux new-session -d -s '$SESSION' -c '$WORKING_DIR' '$COMMAND; echo DONE; read'"

echo "Monitor:  ssh $TARGET \"tmux attach -t $SESSION\""
echo "Logs:     ssh $TARGET \"tmux capture-pane -t $SESSION -p\""
echo "Kill:     ssh $TARGET \"tmux kill-session -t $SESSION\""
```

## Common Commands

```bash
ssh homelab "docker ps"                    # Check services
ssh homelab "docker logs -f service-name"  # View logs
ssh macmini "system_profiler SPHardwareDataType | grep Chip"  # Check GPU
ssh oci-dev "systemctl status my-service"  # Check deployed service
```

## Routing Logic

| Need | Route to |
|------|----------|
| GPU processing, transcription | macmini |
| Docker services, large storage | homelab |
| Cloud APIs, lightweight services | oci-dev |
| Web app deployment | Vercel (not SSH) |
