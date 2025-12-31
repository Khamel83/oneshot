# Public Access: Tailscale Funnel + Cloudflare Worker

Expose homelab services to the public internet with short URLs.

## Architecture

```
khamel.com/fd  ──→  Cloudflare Worker  ──→  302 Redirect
                           ↓
              https://homelab.deer-panga.ts.net/frontdoor
                           ↓
                    Tailscale Funnel
                           ↓
                   Your app on port 8080
```

**No port forwarding. No cert management. No Traefik config.**

## Components

| Component | Purpose | Location |
|-----------|---------|----------|
| Cloudflare Worker | URL shortener/redirector | `~/github/khamel-redirector` |
| Tailscale Funnel | HTTPS tunnel to local port | Any machine on Tailnet |
| Your App | The actual service | Homelab, Mac Mini, etc. |

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

**3. Add route to Cloudflare Worker:**

Edit `~/github/khamel-redirector/src/index.js`:
```javascript
const ROUTES = {
  'fd': 'https://homelab.deer-panga.ts.net/frontdoor/',
  'myservice': 'https://homelab.deer-panga.ts.net/myservice/',  // Add this
};
```

**4. Deploy the worker:**
```bash
cd ~/github/khamel-redirector
source <(sops -d ~/github/oneshot/secrets/secrets.env.encrypted)
npx wrangler deploy
```

**5. Test:**
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
| [khamel-redirector](https://github.com/Khamel83/khamel-redirector) | Cloudflare Worker code |
| [oneshot](https://github.com/Khamel83/oneshot) | Secrets + this documentation |
