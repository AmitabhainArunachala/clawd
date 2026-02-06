# DGC TUI v2.0 — Dharmic Godel Claw Terminal Interface

Enhanced terminal UI for monitoring the DGC (Dhramic Godel Claw) self-modification system with real-time metrics, rich visualization, command palette, and integration monitoring.

## Features

### 🎯 Real-Time Metrics Dashboard
- **Quality Spectrum Visualization** — Live quality level badge with color-coded indicators
- **Metric Gauges** — Visual gauges for R_V, Stability, Genuineness, and Telos coherence
- **Sparkline Charts** — Historical trend visualization for all key metrics
- **Alert System** — Real-time alerts with severity levels and acknowledgment

### 🎨 Enhanced Visualizations
- Color-coded quality levels (Excellent ✨, Good ✅, Degraded ⚠️, Critical 🚨)
- ASCII-based gauge bars with gradient colors
- Sparkline character charts for trend analysis
- Rich terminal UI using Textual framework

### ⌨️ Command Palette (Ctrl+P)
Quick actions via keyboard-driven command palette:
- Refresh Data
- Export Pulse to JSON
- Toggle Auto-refresh
- View Full Report
- Test Gate Passage
- Clear Alerts
- Export History
- Settings / Help

### 🔌 Integration Monitoring
Monitors external DGC integrations:
- Telegram Bot
- FastAPI Dashboard
- Presence Store
- Witness Protocol

Each integration shows:
- Health status (Healthy/Degraded/Unhealthy/Unknown)
- Success/error rates
- Latency measurements
- Last check timestamps

## Installation

```bash
pip install textual rich
```

## Usage

### Basic Usage
```bash
python dgc_tui_v2.py
```

### With Custom Node ID
```bash
python dgc_tui_v2.py --node-id my-node
```

### With Custom Pulse Interval
```bash
python dgc_tui_v2.py --interval 10.0
```

### Demo Mode
```bash
python dgc_tui_v2.py --demo
```

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Ctrl+P` | Open Command Palette |
| `Ctrl+R` | Refresh Dashboard |
| `1` | Switch to Metrics Tab |
| `2` | Switch to Gates Tab |
| `3` | Switch to Integrations Tab |
| `4` | Switch to Logs Tab |
| `Q` | Quit Application |
| `F1` | Show Help |

## Tabs

### 📊 Metrics Tab
Main dashboard showing:
- Quality badge with current level and score
- Four metric gauges (R_V, Stability, Genuineness, Telos)
- Three sparkline charts showing historical trends
- Alert widget with recent notifications
- Statistics panel (uptime, cycles, pulses, gates)

### 🚪 Gates Tab
Gate passage monitoring:
- Gate status overview with health indicators
- Detailed gate metrics table (passages, rejections, rates, health, timing)

### 🔌 Integrations Tab
External integration health:
- Integration status monitor
- Health percentages and latency tracking
- Last check timestamps

### 📝 Logs Tab
Event log with:
- Timestamped events
- Severity levels
- Source attribution

## Architecture

The TUI integrates with the DGC `PresencePulser` system:

```
┌─────────────────────────────────────────────┐
│              DGC TUI v2.0                   │
├─────────────────────────────────────────────┤
│  DashboardScreen                            │
│  ├── Metrics Tab (gauges, sparklines)       │
│  ├── Gates Tab (gate monitoring)            │
│  ├── Integrations Tab (external health)     │
│  └── Logs Tab (event stream)                │
├─────────────────────────────────────────────┤
│  CommandPalette (Ctrl+P)                    │
│  FullReportScreen (detailed report)         │
├─────────────────────────────────────────────┤
│  PresencePulser (from presence_pulse.py)    │
│  ├── PresenceCollector                      │
│  │   ├── MetricHistory (trends)             │
│  │   └── GateMetrics                        │
│  └── Pulse generation & storage             │
└─────────────────────────────────────────────┘
```

## Custom Widgets

### MetricGauge
Visual gauge with color-coded value display.

### SparklineWidget
Character-based sparkline with min/avg/max stats.

### QualityBadge
Quality level display with emoji and color coding.

### GateStatusWidget
Gate health overview with status indicators.

### AlertWidget
Scrollable alert panel with severity colors.

### IntegrationMonitorWidget
Integration health dashboard.

## Data Export

The TUI supports exporting data via the command palette:

- **Export Pulse** — Current pulse as JSON file
- **Export History** — Full pulse history as JSONL

Files are saved with timestamps: `pulse_export_{timestamp}.json`

## Customization

### Theme Colors
Edit `DGCTheme` class to customize colors:

```python
class DGCTheme:
    EXCELLENT = "#00ff88"
    GOOD = "#88ff00"
    DEGRADED = "#ffaa00"
    CRITICAL = "#ff4444"
```

### Adding Integrations
Add to `self.integrations` in `DashboardScreen.__init__`:

```python
self.integrations["my_service"] = IntegrationInfo(
    name="My Service",
    status=IntegrationStatus.HEALTHY,
    ...
)
```

## Integration with Existing DGC

The TUI can connect to an existing DGC instance:

```python
from dgc_tui_v2 import DGCApp
from DHARMIC_GODEL_CLAW.src.core.presence_pulse import PresencePulser

pulser = PresencePulser(node_id="existing-node")
# ... configure pulser ...

app = DGCApp(pulser=pulser)
app.run()
```

## License

Part of DHARMIC_GODEL_CLAW — Dharmic Self-Modification System
