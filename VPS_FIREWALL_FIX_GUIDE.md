# VPS Connectivity & NATS Firewall Fix Guide

## 1. AGNI VPS (157.245.193.15) Diagnosis

### 1.1 Current State Analysis

**Symptoms:**
- SSH timeout on AGNI
- NATS port 4222 blocked
- Tailscale down (10.104.0.2 unreachable)

**Likely Root Causes (in order of probability):**
1. **DigitalOcean Cloud Firewall blocking SSH/NATS**
2. **UFW (Uncomplicated Firewall) misconfigured**
3. **NATS service crashed/failed to start**
4. **Kernel-level iptables rules blocking**
5. **Tailscale daemon down**

---

## 2. EMERGENCY RECOVERY: DigitalOcean Console Access

Since SSH is timing out, use DO's VNC console:

```bash
# Via DigitalOcean Dashboard:
# 1. Go to https://cloud.digitalocean.com/droplets
# 2. Click on AGNI droplet
# 3. Click "Console" button (right side)
# 4. Login with root credentials
```

---

## 3. FIREWALL FIXES

### 3.1 UFW Fix (Immediate - Run on AGNI via Console)

```bash
#!/bin/bash
# save as: fix_ufw.sh
# Run as root on AGNI VPS

echo "=== UFW Firewall Status ==="
ufw status verbose

echo "=== Allowing SSH (port 22) ==="
ufw allow 22/tcp comment 'SSH access'

echo "=== Allowing NATS (port 4222) ==="
ufw allow 4222/tcp comment 'NATS server'

echo "=== Allowing NATS Monitoring (port 8222) ==="
ufw allow 8222/tcp comment 'NATS monitoring'

echo "=== Allowing Tailscale ==="
ufw allow in on tailscale0
ufw allow out on tailscale0

echo "=== Enable UFW if not enabled ==="
ufw --force enable

echo "=== Final Status ==="
ufw status numbered
```

**Run it:**
```bash
chmod +x fix_ufw.sh
./fix_ufw.sh
```

---

### 3.2 DigitalOcean Cloud Firewall Rules

**Via Web UI:**
1. Go to: https://cloud.digitalocean.com/networking/firewalls
2. Select firewall attached to AGNI
3. Add these inbound rules:

| Type | Protocol | Port Range | Sources |
|------|----------|------------|---------|
| SSH | TCP | 22 | YOUR_IP/32, 167.172.95.184/32 |
| Custom TCP | TCP | 4222 | 167.172.95.184/32, 10.104.0.0/16 |
| Custom TCP | TCP | 8222 | YOUR_IP/32 |

**Via DOCTL CLI (from working machine):**
```bash
# Install doctl if needed
# Create/update firewall
doctl compute firewall create \
  --name "agni-firewall" \
  --inbound-rules 'protocol:tcp,ports:22,address:0.0.0.0/0 protocol:tcp,ports:4222,address:167.172.95.184/32 protocol:tcp,ports:8222,address:0.0.0.0/0' \
  --outbound-rules 'protocol:icmp,address:0.0.0.0/0,address:::0/0 protocol:tcp,ports:all,address:0.0.0.0/0,address:::0/0 protocol:udp,ports:all,address:0.0.0.0/0,address:::0/0' \
  --droplet-ids $(doctl compute droplet list --format ID,Name | grep agni | awk '{print $1}')
```

---

### 3.3 Direct iptables Rules (Last Resort)

```bash
#!/bin/bash
# save as: fix_iptables.sh
# Flush and recreate rules

echo "=== Saving current rules ==="
iptables-save > /root/iptables-backup-$(date +%Y%m%d).rules

echo "=== Flushing existing rules ==="
iptables -F
iptables -X
iptables -t nat -F
iptables -t nat -X
iptables -t mangle -F
iptables -t mangle -X

echo "=== Setting default policies ==="
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT

echo "=== Allow loopback ==="
iptables -A INPUT -i lo -j ACCEPT

echo "=== Allow established connections ==="
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

echo "=== Allow SSH ==="
iptables -A INPUT -p tcp --dport 22 -m state --state NEW -j ACCEPT

echo "=== Allow NATS (from RUSHABDEV + Tailscale) ==="
iptables -A INPUT -p tcp --dport 4222 -s 167.172.95.184 -j ACCEPT
iptables -A INPUT -p tcp --dport 4222 -s 10.104.0.0/16 -j ACCEPT

echo "=== Allow NATS monitoring ==="
iptables -A INPUT -p tcp --dport 8222 -j ACCEPT

echo "=== Allow Tailscale interface ==="
iptables -A INPUT -i tailscale0 -j ACCEPT

echo "=== Save rules ==="
iptables-save > /etc/iptables/rules.v4
# OR for systems without iptables-persistent:
# netfilter-persistent save
```

---

## 4. NATS SECURITY CONFIGURATION

### 4.1 Secure NATS Server Config (`nats-server.conf`)

```hcl
# /etc/nats/nats-server.conf
# AGNI VPS - NATS Server Configuration

# === Network ===
port: 4222
net: "0.0.0.0"
server_name: "agni-nats"

# === HTTP Monitoring (localhost only for safety) ===
http_port: 8222

# === Logging ===
logfile: "/var/log/nats/nats-server.log"
log_size_limit: 100MB
log_max_num: 5
log_max_age: 30
debug: false
trace: false

# === Limits ===
max_connections: 1000
max_payload: 8MB
max_pending: 32MB
max_control_line: 4KB

# === Authentication: Credentials File ===
authorization {
  # Users file - create this separately
  users: [
    {
      user: admin
      password: "$2a$11$..."  # bcrypt hash - generate with: mkpasswd -m bcrypt
      permissions: {
        publish: ">"
        subscribe: ">"
      }
    }
    {
      user: rushabdev
      password_from_file: "/etc/nats/.rushabdev_pass"
      permissions: {
        publish: ["events.>", "logs.>"]
        subscribe: ["commands.rushabdev.>", "config.rushabdev"]
      }
    }
    {
      user: agni
      password_from_file: "/etc/nats/.agni_pass"
      permissions: {
        publish: ["events.>", "logs.>"]
        subscribe: ["commands.agni.>", "config.agni"]
      }
    }
  ]
}

# === TLS Configuration (RECOMMENDED) ===
tls {
  cert_file: "/etc/nats/certs/server.crt"
  key_file: "/etc/nats/certs/server.key"
  ca_file: "/etc/nats/certs/ca.crt"
  verify: true
  verify_and_map: true
}

# === Clustering (for future HA) ===
# cluster {
#   port: 6222
#   routes: [
#     "nats-route://167.172.95.184:6222"
#   ]
# }

# === JetStream (persistent messaging) ===
jetstream {
  store_dir: "/var/lib/nats"
  max_memory_store: 1GB
  max_file_store: 10GB
}
```

### 4.2 Setup Script for NATS Security

```bash
#!/bin/bash
# save as: setup_nats_security.sh
# Run as root

NATS_DIR="/etc/nats"
CERTS_DIR="$NATS_DIR/certs"
LOGS_DIR="/var/log/nats"
DATA_DIR="/var/lib/nats"

echo "=== Creating directories ==="
mkdir -p $CERTS_DIR $LOGS_DIR $DATA_DIR
chmod 700 $NATS_DIR $CERTS_DIR

echo "=== Generating passwords ==="
# Generate random passwords
ADMIN_PASS=$(openssl rand -base64 32)
RUSHABDEV_PASS=$(openssl rand -base64 32)
AGNI_PASS=$(openssl rand -base64 32)

# Hash with bcrypt (requires apache2-utils or mkpasswd)
echo "$RUSHABDEV_PASS" > $NATS_DIR/.rushabdev_pass
chmod 600 $NATS_DIR/.rushabdev_pass
echo "$AGNI_PASS" > $NATS_DIR/.agni_pass
chmod 600 $NATS_DIR/.agni_pass

echo "Admin password: $ADMIN_PASS"
echo "RUSHABDEV password: $RUSHABDEV_PASS"
echo "AGNI password: $AGNI_PASS"
echo ""
echo "SAVE THESE PASSWORDS!"

echo "=== Generating TLS certificates ==="
cd $CERTS_DIR

# Generate CA key and cert
openssl genrsa -out ca.key 4096
openssl req -new -x509 -days 3650 -key ca.key -out ca.crt \
  -subj "/C=US/O=AGNI-CA/CN=agni-ca"

# Generate server key and cert
openssl genrsa -out server.key 4096
openssl req -new -key server.key -out server.csr \
  -subj "/C=US/O=AGNI/CN=157.245.193.15" \
  -addext "subjectAltName=IP:157.245.193.15,IP:10.104.0.2,DNS:agni"
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key \
  -CAcreateserial -out server.crt -days 365 \
  -extfile <(echo "subjectAltName=IP:157.245.193.15,IP:10.104.0.2,DNS:agni")

# Generate client cert for RUSHABDEV
openssl genrsa -out rushabdev.key 4096
openssl req -new -key rushabdev.key -out rushabdev.csr \
  -subj "/C=US/O=AGNI/CN=rushabdev"
openssl x509 -req -in rushabdev.csr -CA ca.crt -CAkey ca.key \
  -CAcreateserial -out rushabdev.crt -days 365

chmod 600 *.key
chmod 644 *.crt

echo "=== Setting permissions ==="
chown -R nats:nats $NATS_DIR $LOGS_DIR $DATA_DIR

echo "=== Testing config ==="
nats-server -t -c /etc/nats/nats-server.conf

echo "=== Restarting NATS ==="
systemctl restart nats-server
systemctl status nats-server
```

---

## 5. NETWORK TOPOLOGY RECOMMENDATIONS

### 5.1 Current Issue: AGNI Instability

**Root Cause Analysis:**
```
AGNI (157.245.193.15)
├── Cloud Firewall: ? (unknown state)
├── UFW: Likely blocking 4222
├── NATS: Service may be down
└── Tailscale: Interface down
```

### 5.2 Recommended Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    RECOMMENDED: STAR TOPOLOGY                 │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│    ┌──────────────┐                                          │
│    │   AGNI       │ ◄──── PRIMARY NATS SERVER                 │
│    │  157.245...  │      (after recovery)                     │
│    │  [NATS]      │                                          │
│    └──────┬───────┘                                          │
│           │                                                  │
│           │ Tailscale (10.104.0.x)                           │
│           │ OR Private Network                                 │
│           │                                                  │
│    ┌──────┴───────┐                                          │
│    │ RUSHABDEV    │ ◄──── CLIENT / POTENTIAL BACKUP           │
│    │ 167.172...   │                                          │
│    └──────────────┘                                          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 5.3 Decision Matrix

| Option | Pros | Cons | When to Choose |
|--------|------|------|----------------|
| **AGNI as NATS Server** | Single source of truth, simple | Single point of failure | AGNI is stable |
| **RUSHABDEV as NATS Server** | AGNI can be client/recover | Need to migrate configs | AGNI keeps failing |
| **Mesh (Both run NATS)** | HA, no single point | Complex clustering | Production critical |
| **DO Managed NATS** | Fully managed, HA | $$$, vendor lock-in | Budget allows, want zero ops |
| **Synadia Cloud** | Enterprise features | External dependency | Need advanced features |

### 5.4 My Recommendation: Star Topology with AGNI Recovery

**Step 1:** Fix AGNI (this is likely a simple firewall issue)
**Step 2:** Implement TLS + Auth
**Step 3:** Add RUSHABDEV as backup NATS server for HA

### 5.5 RUSHABDEV as Backup NATS Server (Optional)

If you want to switch primary NATS to RUSHABDEV:

```bash
# On RUSHABDEV (167.172.95.184)
# Copy the same nats-server.conf but change:
server_name: "rushabdev-nats"

# Update cluster section:
cluster {
  port: 6222
  routes: [
    "nats-route://157.245.193.15:6222"
  ]
}
```

---

## 6. TAILSCALE FIX

```bash
#!/bin/bash
# fix_tailscale.sh

echo "=== Tailscale Status ==="
tailscale status

echo "=== Restarting Tailscale ==="
systemctl restart tailscaled
sleep 2

echo "=== Check if authenticated ==="
tailscale status
if [ $? -ne 0 ]; then
    echo "Need to re-authenticate:"
    tailscale up
fi

echo "=== Verify interface ==="
ip addr show tailscale0

echo "=== Test connectivity ==="
ping -c 3 10.104.0.1  # Replace with other node's tailscale IP
```

---

## 7. COMPLETE RECOVERY CHECKLIST

```
□ Step 1: Access AGNI via DO Console
  └─ https://cloud.digitalocean.com/droplets → Console

□ Step 2: Check service status
  ├─ systemctl status sshd
  ├─ systemctl status nats-server
  ├─ systemctl status tailscaled
  └─ systemctl status ufw

□ Step 3: Fix UFW
  ├─ ufw allow 22/tcp
  ├─ ufw allow 4222/tcp
  ├─ ufw allow in on tailscale0
  └─ ufw reload

□ Step 4: Fix NATS config
  ├─ Write /etc/nats/nats-server.conf
  ├─ Generate TLS certs
  ├─ Set permissions
  └─ systemctl restart nats-server

□ Step 5: Verify from RUSHABDEV
  ├─ nc -zv 157.245.193.15 22
  ├─ nc -zv 157.245.193.15 4222
  └─ nats --server nats://rushabdev:PASS@157.245.193.15:4222 ping

□ Step 6: Update DO Cloud Firewall
  └─ Add 4222 rule for RUSHABDEV IP

□ Step 7: Fix Tailscale
  ├─ systemctl restart tailscaled
  ├─ tailscale up
  └─ ping 10.104.0.X (other node)
```

---

## 8. MANAGED NATS ALTERNATIVES

### 8.1 DigitalOcean Managed NATS (App Platform)

```bash
# Create via UI:
# https://cloud.digitalocean.com/apps/new
# Select "NATS" from the components

# Pricing: ~$12/month for basic
# Pros: HA, backups, managed
# Cons: Network egress costs
```

### 8.2 Synadia Cloud (NATS.io Commercial)

```bash
# https://www.synadia.com/
# Enterprise NATS with global deployment
# Pricing: Custom (typically $100+/month)
# Best for: Multi-region, enterprise features
```

### 8.3 Self-Managed with Docker Compose

```yaml
# docker-compose.yml for quick HA setup
version: '3'
services:
  nats-1:
    image: nats:2.10-alpine
    ports:
      - "4222:4222"
      - "8222:8222"
    command: >
      --server_name nats-1
      --jetstream
      --store_dir /data
      --cluster_name agni-cluster
      --cluster nats://0.0.0.0:6222
      --routes nats://nats-2:6222
      --http_port 8222
    volumes:
      - ./nats-data-1:/data
      - ./nats-server.conf:/etc/nats/nats-server.conf
      
  nats-2:
    image: nats:2.10-alpine
    command: >
      --server_name nats-2
      --jetstream
      --store_dir /data
      --cluster_name agni-cluster
      --cluster nats://0.0.0.0:6222
      --routes nats://nats-1:6222
    volumes:
      - ./nats-data-2:/data
```

---

## 9. QUICK COMMANDS REFERENCE

### UFW
```bash
ufw status numbered          # Show rules with numbers
ufw delete 3                 # Delete rule #3
ufw allow from 167.172.95.184 to any port 4222
ufw deny 4222/tcp            # Block port
ufw reset                    # Reset to defaults (DANGER)
```

### NATS
```bash
# Test connection
nats --server nats://IP:4222 ping

# Subscribe	nats --server nats://IP:4222 sub "test.>"

# Publish
nats --server nats://IP:4222 pub test.msg "hello"

# Check server info
nats --server nats://IP:4222 server info
```

### Tailscale
```bash
tailscale status             # Show node status
tailscale ip -4              # Show tailscale IP
tailscale ping NODE          # Test connectivity
tailscale up --advertise-routes=10.0.0.0/8
```

---

## SUMMARY

**Most Likely Fix:**
1. UFW is blocking port 4222
2. Run the fix_ufw.sh script via DO Console
3. Verify with nc from RUSHABDEV

**For Security:**
1. Implement the nats-server.conf with TLS
2. Use credentials files, not plaintext passwords
3. Restrict DO Cloud Firewall to known IPs only

**Topology Recommendation:**
- Keep AGNI as primary NATS server (it's likely just a firewall issue)
- Add RUSHABDEV as a cluster node for HA
- Use Tailscale for secure inter-node communication
