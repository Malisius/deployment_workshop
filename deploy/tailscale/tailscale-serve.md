# Tailscale Serve & Tailscale Funnel Guide

Tailscale offers two powerful features to expose your self-hosted Flask application:

1. **Tailscale Serve**: Shares your local service privately with other devices on your Tailscale private mesh network (tailnet).
2. **Tailscale Funnel**: Routes public internet traffic through Tailscale's global edge proxies directly to your local node, with **automatic HTTPS Let's Encrypt certificates** and **zero port forwarding required** (bypasses CGNAT, firewalls, and dynamic IPs).

---

## 1. Tailscale Serve (Private Mesh Network Only)

To expose your application only to devices authenticated in your Tailnet:

```bash
# Ensure Tailscale is running
sudo tailscale up

# Serve port 5000 over HTTPS within your tailnet
sudo tailscale serve --bg 5000
```

Access your app via:
`https://<node-name>.<tailnet-name>.ts.net`

To view active serve status:
```bash
tailscale serve status
```

To stop serving:
```bash
tailscale serve reset
```

---

## 2. Tailscale Funnel (Public Internet Exposure with Auto-HTTPS)

Tailscale Funnel allows public visitors anywhere on the internet to reach your local service.

### Prerequisites:
1. Enable Funnel in your Tailscale Admin Console:
   - Go to **Access Controls** (ACLs) in the Tailscale admin console.
   - Add the Funnel attribute:
     ```json
     "nodeAttrs": [
       {
         "target": ["autogroup:members"],
         "attr": ["funnel"]
       }
     ]
     ```
2. Enable **MagicDNS** and **HTTPS Certificates** in the **DNS** settings tab.

### Exposing the App:
```bash
# Turn on Funnel for local port 5000 (listens on port 443 with auto-SSL)
sudo tailscale funnel --bg 5000
```

Your service is now live on the public internet at:
`https://<node-name>.<tailnet-name>.ts.net`

### Managing Funnel:
```bash
# Check status
tailscale funnel status

# Turn off Funnel
tailscale funnel reset
```

---

## 3. Persistent Systemd Integration

Tailscale retains its serve and funnel state across reboots automatically once started with `--bg`. If you want an explicit systemd unit that activates on boot alongside your app, Tailscale is already managed by `tailscaled.service`.
