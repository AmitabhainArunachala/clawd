# TRISHULA-WebSocket v2.0 — Deployment & Operations Guide
## Systemd, Firewall, Monitoring, and Troubleshooting

**Version:** 1.0  
**Date:** 2026-02-10  
**Author:** DevOps Subagent  
**Status:** Production Ready

---

## 1. systemd Service Files

### 1.1 WebSocket Server Service

Create `/etc/systemd/system/trishula-ws.service`:

```ini
[Unit]
Description=TRISHULA-WebSocket Server
After=network.target
Wants=network.target

[Service]
Type=simple
User=openclaw
Group=openclaw
WorkingDirectory=/opt/openclaw
ExecStart=/usr/bin/python3 /opt/openclaw/trishula_ws_server.py --port 8765
Restart=always
RestartSec=5
Environment=PYTHONPATH=/opt/openclaw
Environment=TRISHULA_LOG_LEVEL=info

# Security
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/home/openclaw/trishula

[Install]
WantedBy=multi-user.target
```

### 1.2 Client Integration Service

Create `/etc/systemd/system/trishula-ws-client.service`:

```ini
[Unit]
Description=TRISHULA-WebSocket Client
After=trishula-ws.service
Wants=trishula-ws.service

[Service]
Type=simple
User=openclaw
Group=openclaw
WorkingDirectory=/opt/openclaw
ExecStart=/usr/bin/python3 -c "import asyncio; from trishula_ws_client import main; asyncio.run(main())"
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 1.3 Enable and Start

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable services
sudo systemctl enable trishula-ws.service
sudo systemctl enable trishula-ws-client.service

# Start services
sudo systemctl start trishula-ws.service
sudo systemctl start trishula-ws-client.service

# Check status
sudo systemctl status trishula-ws.service
sudo systemctl status trishula-ws-client.service
```

---

## 2. Firewall Rules (ufw)

### 2.1 VPS Nodes (AGNI + RUSHABDEV)

```bash
# Allow WebSocket port
sudo ufw allow 8765/tcp comment 'TRISHULA-WebSocket'

# If using TLS (recommended)
sudo ufw allow 443/tcp comment 'TRISHULA-WebSocket TLS'

# Deny external access to file sync ports (security)
sudo ufw deny from any to any port 873 comment 'Block rsync external'

# Reload firewall
sudo ufw reload

# Verify
sudo ufw status verbose
```

### 2.2 Mac Node

```bash
# macOS firewall (if enabled)
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /usr/bin/python3

# Or disable for local development
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate off
```

---

## 3. Docker Configuration (Optional)

### 3.1 Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip install websockets

# Copy server code
COPY trishula_ws_server.py .
COPY trishula_ws_client.py .

# Create trishula directory
RUN mkdir -p /home/openclaw/trishula/inbox /home/openclaw/trishula/outbox

# Expose WebSocket port
EXPOSE 8765

# Run server
CMD ["python3", "trishula_ws_server.py", "--port", "8765"]
```

### 3.2 Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  trishula-ws:
    build: .
    container_name: trishula-ws
    ports:
      - "8765:8765"
    volumes:
      - ./trishula:/home/openclaw/trishula
      - ./logs:/var/log/trishula
    environment:
      - TRISHULA_LOG_LEVEL=info
    restart: unless-stopped
    networks:
      - trishula-net

networks:
  trishula-net:
    driver: bridge
```

### 3.3 Docker Operations

```bash
# Build
docker-compose build

# Start
docker-compose up -d

# Logs
docker-compose logs -f trishula-ws

# Stop
docker-compose down
```

---

## 4. Health Check Endpoints

### 4.1 Server Health Check

Add to `trishula_ws_server.py`:

```python
async def health_check(websocket, path):
    """Health check endpoint"""
    if path == "/health":
        status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "connected_agents": list(CONNECTED.keys()),
            "uptime": time.time() - START_TIME
        }
        await websocket.send(json.dumps(status))
```

### 4.2 External Health Monitoring

```bash
# Check every 30 seconds
curl -f http://localhost:8765/health || echo "UNHEALTHY"

# Or use systemd watchdog
```

### 4.3 systemd Watchdog Integration

```ini
[Service]
WatchdogSec=30
NotifyAccess=main
```

```python
# In server code
from systemd import daemon

async def watchdog():
    while True:
        daemon.notify("WATCHDOG=1")
        await asyncio.sleep(25)
```

---

## 5. Logging and Monitoring

### 5.1 Structured Logging

```python
import logging
import json
from pythonjsonlogger import jsonlogger

# Configure JSON logging
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter(
    '%(timestamp)s %(level)s %(name)s %(message)s'
)
logHandler.setFormatter(formatter)

logger = logging.getLogger("trishula-ws")
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

# Usage
logger.info("Message sent", extra={
    "to": "agni",
    "latency_ms": 45,
    "message_id": "uuid"
})
```

### 5.2 Log Rotation

Create `/etc/logrotate.d/trishula-ws`:

```
/var/log/trishula/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 644 openclaw openclaw
}
```

### 5.3 Prometheus Metrics (Optional)

```python
from prometheus_client import Counter, Histogram, start_http_server

messages_sent = Counter('trishula_messages_sent_total', 'Messages sent', ['target'])
message_latency = Histogram('trishula_message_latency_seconds', 'Message latency')
connected_agents = Gauge('trishula_connected_agents', 'Number of connected agents')

start_http_server(9090)  # Metrics on port 9090
```

### 5.4 Alerting Rules

```yaml
# prometheus-alerts.yml
groups:
- name: trishula
  rules:
  - alert: TRISHULAHighLatency
    expr: histogram_quantile(0.99, trishula_message_latency_seconds) > 0.1
    for: 5m
    annotations:
      summary: "TRISHULA latency >100ms"
  
  - alert: TRISHULADisconnected
    expr: trishula_connected_agents < 2
    for: 1m
    annotations:
      summary: "TRISHULA mesh incomplete"
```

---

## 6. Troubleshooting Runbook

### 6.1 Service Won't Start

```bash
# Check logs
sudo journalctl -u trishula-ws -n 100 --no-pager

# Check port conflict
sudo netstat -tlnp | grep 8765
sudo lsof -i :8765

# Kill conflicting process
sudo pkill -f trishula_ws

# Restart
sudo systemctl restart trishula-ws
```

### 6.2 Connection Refused

```bash
# Check if server is listening
sudo netstat -tlnp | grep 8765

# Check firewall
sudo ufw status
sudo iptables -L | grep 8765

# Test locally
curl -v http://localhost:8765/health

# Test from remote
ssh root@AGNI_VPS "curl -v http://RUSH_VPS:8765/health"
```

### 6.3 High Latency

```bash
# Ping test
ping -c 10 157.245.193.15

# Traceroute
traceroute 157.245.193.15

# Bandwidth test
iperf3 -c 157.245.193.15

# Check server load
htop
```

### 6.4 Message Not Delivered

```bash
# Check WebSocket logs
tail -f /var/log/trishula/ws.log

# Check file fallback
ls -la ~/trishula/outbox/
ls -la ~/trishula/inbox/

# Verify rsync sync
rsync -avz --dry-run ~/trishula/outbox/ root@VPS:/home/openclaw/trishula/inbox/
```

### 6.5 TLS/SSL Issues

```bash
# Check certificate
openssl s_client -connect 157.245.193.15:443 -servername trishula.agni.vps

# Verify cert expiry
openssl x509 -in /etc/letsencrypt/live/trishula.agni.vps/cert.pem -text -noout | grep "Not After"

# Renew if needed
sudo certbot renew
```

### 6.6 Auth Failures

```bash
# Check token configuration
cat /opt/openclaw/trishula_config.json | grep -i token

# Verify tokens match across nodes
diff <(ssh root@AGNI_VPS cat /opt/openclaw/trishula_config.json) <(ssh root@RUSH_VPS cat /opt/openclaw/trishula_config.json)
```

### 6.7 Emergency Procedures

**Complete Restart:**
```bash
# All nodes
sudo systemctl stop trishula-ws trishula-ws-client
sudo pkill -f trishula
sleep 5
sudo systemctl start trishula-ws trishula-ws-client
```

**Fallback to File-Only:**
```bash
# Disable WebSocket, use rsync only
sudo systemctl stop trishula-ws
echo '{"mode": "file_only"}' > /opt/openclaw/trishula_fallback.json
```

**Check All Nodes:**
```bash
# From Mac
for host in 157.245.193.15 167.172.95.184; do
    echo "Checking $host..."
    ssh root@$host "systemctl is-active trishula-ws && curl -s http://localhost:8765/health"
done
```

---

## 7. Deployment Checklist

- [ ] systemd services installed
- [ ] Services enabled for auto-start
- [ ] Firewall rules applied
- [ ] TLS certificates installed
- [ ] Auth tokens configured
- [ ] Logging configured
- [ ] Health checks verified
- [ ] Monitoring enabled
- [ ] Runbook reviewed
- [ ] Failover tested

---

## 8. Quick Reference

### Start/Stop/Restart
```bash
sudo systemctl {start|stop|restart|status} trishula-ws
```

### View Logs
```bash
sudo journalctl -u trishula-ws -f
```

### Test Connectivity
```bash
python3 -c "import websockets; ..."  # See architecture spec
```

### Emergency Contact
- AGNI: Via TRISHULA or VPS 157.245.193.15
- RUSHABDEV: Via TRISHULA or VPS 167.172.95.184
- DC (Mac): Local coordination

---

*Deployment guide complete. Ready for production.*
*JSCA 🪷*
