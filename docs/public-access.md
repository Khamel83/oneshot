# Public Access: Tailscale Funnel + Cloudflare Worker

> **Canonical documentation**: [poytz README](https://github.com/Khamel83/poytz)
>
> This file is a summary. The poytz repo is the source of truth for all public URL routing.
>
> **Historical note**: The previous implementation was [khamel-redirector](https://github.com/Khamel83/khamel-redirector), now archived.

## What It Is

**poytz** is a personal cloud infrastructure platform on Cloudflare Workers. All public traffic goes through `khamel.com/*`.

```
khamel.com/photos  →  302 redirect  →  https://homelab.deer-panga.ts.net/photos/
khamel.com/blog    →  302 redirect  →  https://myblog.com/
```

**This replaces**: Traefik, nginx reverse proxy, complex DNS configs, SSL cert management.

## Quick Reference

### Current Routes

| Short URL | Target | Machine |
|-----------|--------|---------|
| `khamel.com/fd` | front-door web app | homelab:8080 |

### Add a New Service

**1. Start your app locally:**
```bash
# Example: FastAPI on port 8080
uvicorn app:app --host 127.0.0.1 --port 8080
```

**2. Expose via Tailscale Funnel:**
```bash
# One-time setup (runs in background)
sudo tailscale funnel --bg --set-path=/myservice http://localhost:8080
```

**3. Add route via poytz API:**
```bash
# Add route dynamically
curl -X POST https://khamel.com/api/routes \
  -H "X-API-Key: $POYTZ_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"path": "myservice", "target": "https://homelab.deer-panga.ts.net/myservice/"}'
```

Or use the web UI at `https://khamel.com/admin`

**4. Test:**
```bash
curl -I https://khamel.com/myservice
```

## Tailscale Funnel Commands

```bash
# Start funnel for a path
sudo tailscale funnel --bg --set-path=/path http://localhost:PORT

# Check status
tailscale serve status

# Stop funnel for a path
sudo tailscale funnel --set-path=/path off

# Stop all funnels
sudo tailscale funnel reset
```

## Systemd Integration

For persistent services, create a systemd unit:

```bash
# /etc/systemd/system/myservice.service
[Unit]
Description=My Service
After=network.target

[Service]
Type=simple
User=khamel83
WorkingDirectory=/home/khamel83/dev/myservice
ExecStart=/home/khamel83/dev/myservice/venv/bin/uvicorn app:app --host 127.0.0.1 --port 8080
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable --now myservice
```

## Comparison: Traefik vs Funnel

| Aspect | Traefik | Tailscale Funnel |
|--------|---------|------------------|
| **Setup complexity** | Docker labels, cert config | One command |
| **Port forwarding** | Required | None |
| **SSL Certs** | Let's Encrypt, renewal | Automatic (Tailscale) |
| **Add new service** | Edit compose, add labels | `tailscale funnel` + 1 line |
| **Move to new machine** | DNS + Traefik reconfig | Change 1 line in Worker |
| **Debugging** | Check Traefik logs, certs | `tailscale funnel status` |

**Use Traefik for**: Complex routing, multiple domains, load balancing
**Use Funnel for**: Simple services, quick deploys, homelab apps

## Secrets Required

| Secret | In | Purpose |
|--------|-----|---------|
| `CLOUDFLARE_API_TOKEN` | `secrets.env.encrypted` | Deploy workers |
| `CLOUDFLARE_ZONE_ID_KHAMEL` | `secrets.env.encrypted` | Zone ID for khamel.com |

## Troubleshooting

### 404 from khamel.com

Your DNS is cached. Try:
- Phone on cellular (not WiFi)
- Flush DNS: `sudo systemd-resolve --flush-caches`
- Check public DNS: `dig khamel.com @8.8.8.8`

### Funnel not responding

```bash
# Check if funnel is running
tailscale serve status

# Check if app is listening
curl http://localhost:8080

# Check systemd service
sudo systemctl status myservice
```

### Worker not deploying

```bash
# Verify token works
curl -s https://api.cloudflare.com/client/v4/user/tokens/verify \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" | jq .success
```

## Repositories

| Repo | Purpose |
|------|---------|
| [poytz](https://github.com/Khamel83/poytz) | Cloudflare Worker + API + UI |
| [khamel-redirector](https://github.com/Khamel83/khamel-redirector) | **ARCHIVED** - Previous implementation |
| [oneshot](https://github.com/Khamel83/oneshot) | Secrets + this documentation |
