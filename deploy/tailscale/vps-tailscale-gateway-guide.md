# VPS Ingress Reverse Proxy over Tailscale Mesh

## Overview & Architecture

This pattern allows you to self-host your web application and database on your home server (or homelab/office hardware) while:
1. **Completely hiding your home IP address** from public DNS records and web visitors.
2. **Dodging dynamic IP issues** without needing Dynamic DNS (DDNS) scripts, because Tailscale automatically handles IP roaming in the background.
3. **Bypassing Carrier-Grade NAT (CGNAT)** without opening a single inbound port on your home router.
4. **Terminating public SSL/TLS certificates** cleanly on a cheap cloud VPS using standard Certbot / Let's Encrypt.

```
+-----------------------------------------------------------------------------------+
|                                  PUBLIC INTERNET                                  |
+-----------------------------------------------------------------------------------+
                                          |
                        DNS A Record: workshop.yourdomain.com
                                 Points to VPS Public IP
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                        CLOUD VPS (e.g. $3.50/mo Hetzner/DO)                       |
|                                                                                   |
|  - Public Static IP: 203.0.113.50                                                 |
|  - Nginx Reverse Proxy (Listening on 80 & 443)                                    |
|  - Let's Encrypt SSL Certificate (Managed by Certbot)                             |
|  - Tailscale Client: Authenticated to your Tailnet (e.g. 100.64.0.1)               |
+-----------------------------------------------------------------------------------+
                                          |
                         ENCRYPTED TAILSCALE MESH (WireGuard)
                     Traffic routed securely via Tailscale overlay
                        (Bypasses Home Router Firewall & CGNAT)
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                     HOME SERVER (Your Physical Hardware/Lab)                      |
|                                                                                   |
|  - Home ISP: Dynamic IP / Behind CGNAT (Completely hidden from public!)           |
|  - Router Firewall: ZERO inbound ports opened!                                    |
|  - Tailscale Client: Authenticated to same Tailnet (e.g. 100.101.102.103)         |
|  - Flask Application: Running on 127.0.0.1:5000 or 100.101.102.103:5000           |
|  - MySQL 8.0: Running locally / in Docker container                               |
+-----------------------------------------------------------------------------------+
```

---

## Step-by-Step Implementation Guide

### Phase 1: Prepare the Home Server

1. **Install and Connect Tailscale**:
   ```bash
   curl -fsSL https://tailscale.com/install.sh | sh
   sudo tailscale up
   ```
2. **Get your Home Server's Tailscale IP**:
   ```bash
   tailscale ip -4
   # Example output: 100.101.102.103
   ```
3. **Run your Flask App and MySQL Database**:
   - Using Docker Compose:
     ```bash
     docker compose up -d
     ```
     Ensure the web port is mapped to `0.0.0.0:5000` or specifically to your Tailscale IP `100.101.102.103:5000`.
   - Or using Systemd:
     Ensure Gunicorn binds to `0.0.0.0:5000` or `100.101.102.103:5000` in `/etc/systemd/system/deployment-workshop.service`.
4. **Lock Down the Home Server Firewall (UFW)**:
   Ensure port 5000 is **only** accessible from the Tailscale network interface:
   ```bash
   # Block all arbitrary incoming connections by default
   sudo ufw default deny incoming
   sudo ufw default allow outgoing

   # Allow SSH over local network or Tailscale only
   sudo ufw allow in on tailscale0 to any port 22 proto tcp

   # Allow port 5000 ONLY on the Tailscale interface
   sudo ufw allow in on tailscale0 to any port 5000 proto tcp

   sudo ufw enable
   ```
   *Notice: You do NOT touch your home router's port forwarding settings! All router ports remain closed.*

---

### Phase 2: Prepare the Cloud VPS Gateway

1. **Provision a minimal Linux VPS** (Ubuntu 22.04 or 24.04 LTS) with a public static IP address.
2. **Install Nginx, Certbot, and Tailscale**:
   ```bash
   sudo apt-get update
   sudo apt-get install -y nginx certbot python3-certbot-nginx curl
   curl -fsSL https://tailscale.com/install.sh | sh
   sudo tailscale up
   ```
3. **Verify Tailscale Connectivity to Home Server**:
   From the VPS, ping your home server's Tailscale IP:
   ```bash
   ping 100.101.102.103
   curl -I http://100.101.102.103:5000/healthz
   ```
   You should receive an HTTP 200 OK response from the Flask application running in your living room!

---

### Phase 3: Configure Public DNS

In your domain's DNS provider (Cloudflare, Namecheap, Route53, etc.):
- Create an **A record**:
  - **Host / Name**: `workshop` (or `@` for apex domain)
  - **Points to / Value**: `YOUR_VPS_PUBLIC_IP` (e.g., `203.0.113.50`)
  - **TTL**: Auto or 300 seconds

*Notice: Your home IP address never appears in DNS. Anyone doing `dig workshop.yourdomain.com` or `nslookup` only sees the cloud VPS.*

---

### Phase 4: Obtain SSL Certificate on the VPS

On the VPS, obtain a free SSL certificate for your domain using Certbot:
```bash
# Allow HTTP/HTTPS traffic through the VPS firewall
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow OpenSSH
sudo ufw enable

# Obtain certificate using the Nginx plugin
sudo certbot certonly --nginx -d workshop.yourdomain.com
```

Certbot places the certificate at:
`/etc/letsencrypt/live/workshop.yourdomain.com/fullchain.pem`

---

### Phase 5: Install Nginx Reverse Proxy on the VPS

1. Copy the template from this repository to the VPS:
   ```bash
   sudo cp deploy/tailscale/vps_nginx_tailscale_ingress.conf /etc/nginx/sites-available/workshop.conf
   ```
2. Edit `/etc/nginx/sites-available/workshop.conf`:
   - Replace `workshop.yourdomain.com` with your actual domain.
   - Update `proxy_pass http://100.x.y.z:5000;` with your Home Server's Tailscale IP (e.g. `http://100.101.102.103:5000;`).
3. Enable the site and restart Nginx:
   ```bash
   sudo ln -sf /etc/nginx/sites-available/workshop.conf /etc/nginx/sites-enabled/
   sudo rm -f /etc/nginx/sites-enabled/default
   sudo nginx -t
   sudo systemctl reload nginx
   ```

---

## Why this Architecture Completely Dodges Dynamic IP Issues

1. **No DDNS Delay**: When your home ISP changes your public IP address, traditional Dynamic DNS takes several minutes (or hours due to DNS TTL caching) to update. During that window, your site is down or points to someone else's IP.
2. **WireGuard Roaming**: Tailscale uses WireGuard under the hood with built-in endpoint roaming and DERP relays. When your home server's ISP rotates its IP address, Tailscale detects the network change within milliseconds, re-negotiates the direct peer-to-peer WireGuard tunnel with the VPS, and traffic continues flowing without dropping active user sessions.
3. **Zero Inbound Port Scanning**: Shodan, Censys, and malicious scanners only scan your VPS. Your home network is completely invisible to the public internet.

---

## Security Hardening: Tailscale ACLs

In your Tailscale Admin Console -> **Access Controls**, you can restrict the VPS so that it can **only** contact port 5000 on your home server and cannot access any other home devices (like your NAS, laptops, or smart TVs):

```json
{
  "acls": [
    {
      "action": "accept",
      "src": ["tag:vps-gateway"],
      "dst": ["tag:home-server:5000"]
    }
  ],
  "tagOwners": {
    "tag:vps-gateway": ["autogroup:admin"],
    "tag:home-server": ["autogroup:admin"]
  }
}
```
This guarantees that even if the public-facing VPS were ever compromised, an attacker could not pivot into your private home network.
