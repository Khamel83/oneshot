# /deploy — Push to OCI-Dev Cloud

Deploy the current project to oci-dev (100.126.13.70) via SSH.

## Target: OCI-Dev

| Property | Value |
|----------|-------|
| SSH Alias | `oci-dev` |
| User | ubuntu |
| Tailscale IP | 100.126.13.70 |
| OS | Ubuntu 24.04 LTS (ARM64) |
| Free: 4 OCPU, 24GB RAM, 200GB disk, 10TB/month outbound |

## Deploy Script

```bash
PROJECT_NAME="my-project"
PORT="8080"
ENTRY_POINT="app.py"

# 1. Push code
rsync -avz --exclude='.venv' --exclude='node_modules' \
  --exclude='__pycache__' --exclude='.git' \
  ./ ubuntu@100.126.13.70:~/dev/${PROJECT_NAME}/

# 2. Setup on remote
ssh oci-dev << REMOTE
cd ~/dev/${PROJECT_NAME}
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Create systemd service
sudo tee /etc/systemd/system/${PROJECT_NAME}.service > /dev/null << SERVICE
[Unit]
Description=${PROJECT_NAME}
After=network.target
[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/dev/${PROJECT_NAME}
ExecStart=/home/ubuntu/dev/${PROJECT_NAME}/venv/bin/python ${ENTRY_POINT}
Restart=always
RestartSec=5
Environment=PORT=${PORT}
[Install]
WantedBy=multi-user.target
SERVICE

sudo systemctl daemon-reload
sudo systemctl enable ${PROJECT_NAME}
sudo systemctl restart ${PROJECT_NAME}
sleep 2
systemctl is-active --quiet ${PROJECT_NAME} && echo "Running" || echo "Failed"
REMOTE
```

## Steps

1. Determine project type (Python service, web app, static site)
2. Ensure tests pass locally before deploying
3. Web apps → Vercel, not oci-dev. Redirect user.
4. rsync project files
5. Create/update systemd unit, install deps in venv, restart
6. Verify: `ssh oci-dev 'systemctl status <project-name>'`
7. If public access needed: Tailscale Funnel (not nginx/traefik)

## Service Management

```bash
ssh oci-dev "systemctl status $NAME"      # Status
ssh oci-dev "journalctl -u $NAME -f"      # Logs
ssh oci-dev "sudo systemctl restart $NAME" # Restart
```

## Rollback

```bash
ssh oci-dev "sudo systemctl stop $NAME && sudo systemctl disable $NAME"
ssh oci-dev "sudo rm /etc/systemd/system/$NAME.service && sudo systemctl daemon-reload"
ssh oci-dev "rm -rf ~/dev/$NAME"
```
