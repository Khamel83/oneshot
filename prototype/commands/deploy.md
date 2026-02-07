# /deploy — Push to oci-dev

Deploy the current project to oci-dev (100.126.13.70) via SSH.

## Steps

1. Determine project type (Python service, web app, static site)
2. Ensure tests pass locally before deploying
3. rsync project files to oci-dev: `rsync -avz --exclude='.git' --exclude='node_modules' --exclude='__pycache__' ./ oci-dev:~/services/<project-name>/`
4. SSH to oci-dev and set up:
   - For Python services: create/update systemd unit, install deps in venv, restart service
   - For web apps: these go to Vercel, not oci-dev — redirect user
5. Verify the service is running: `ssh oci-dev 'systemctl status <project-name>'`
6. If public access needed: configure Tailscale Funnel via `tailscale funnel`

## Prerequisites
- SSH access to oci-dev configured (key-based)
- Project has a working entrypoint
