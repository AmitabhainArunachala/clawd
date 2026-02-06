#!/usr/bin/env python3
"""
dgc_tui_v2.py — Dharmic Godel Claw TUI Interface v2.0

Enhanced terminal interface with:
- Real-time metrics dashboard
- Rich visualizations (sparklines, gauges, heatmaps)
- Command palette for quick actions
- Integration monitoring for all DGC components
- Quality spectrum visualization
- Gate passage monitoring

Part of: DHARMIC_GODEL_CLAW — Dharmic Self-Modification System
"""

import asyncio
import json
import time
import threading
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Callable, Any, Tuple, Set
from collections import deque
from pathlib import Path

# Textual imports
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, Grid
from textual.widgets import (
    Header, Footer, Static, DataTable, Log, ProgressBar,
    Sparkline, Label, Button, Input, ListView, ListItem,
    TabbedContent, TabPane, Tree, Switch, Select, Checkbox,
    OptionList, Rule, Collapsible, ContentSwitcher
)
from textual.reactive import reactive
from textual.binding import Binding
from textual.worker import Worker, get_current_worker
from textual.color import Color
from textual.screen import Screen, ModalScreen
from textual.coordinate import Coordinate

# Rich imports for enhanced display
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich.layout import Layout
from rich.syntax import Syntax
from rich.json import JSON

# Import DGC core
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from DHARMIC_GODEL_CLAW.src.core.presence_pulse import (
    PresenceCollector, PresencePulse, PresencePulser,
    QualityLevel, GateMetrics, MetricHistory, TelegramWitnessIntegration
)


# ═══════════════════════════════════════════════════════════════════════════
# DATA MODELS & STATE
# ═══════════════════════════════════════════════════════════════════════════

class IntegrationStatus(Enum):
    """Status for external integrations."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"
    DISABLED = "disabled"


@dataclass
class IntegrationInfo:
    """Information about an external integration."""
    name: str
    status: IntegrationStatus
    last_check: float
    latency_ms: float
    error_count: int
    success_count: int
    details: Dict[str, Any]
    
    @property
    def health_percent(self) -> float:
        total = self.success_count + self.error_count
        if total == 0:
            return 100.0
        return (self.success_count / total) * 100


@dataclass
class AlertEvent:
    """Alert/event notification."""
    timestamp: float
    level: str  # info, warning, error, critical
    source: str
    message: str
    acknowledged: bool = False
    
    @property
    def age_seconds(self) -> int:
        return int(time.time() - self.timestamp)


# ═══════════════════════════════════════════════════════════════════════════
# THEME & STYLING
# ═══════════════════════════════════════════════════════════════════════════

class DGCTheme:
    """DGC TUI color theme."""
    # Quality colors
    EXCELLENT = "#00ff88"
    GOOD = "#88ff00"
    DEGRADED = "#ffaa00"
    CRITICAL = "#ff4444"
    UNKNOWN = "#888888"
    
    # Semantic colors
    PRIMARY = "#6b8cff"
    SECONDARY = "#a855f7"
    SUCCESS = "#22c55e"
    WARNING = "#f59e0b"
    ERROR = "#ef4444"
    INFO = "#3b82f6"
    
    # UI colors
    BACKGROUND = "#0f0f1a"
    SURFACE = "#1a1a2e"
    BORDER = "#2a2a3e"
    TEXT = "#e2e8f0"
    TEXT_MUTED = "#64748b"
    
    @classmethod
    def quality_color(cls, level: str) -> str:
        """Get color for quality level."""
        return {
            QualityLevel.EXCELLENT.value: cls.EXCELLENT,
            QualityLevel.GOOD.value: cls.GOOD,
            QualityLevel.DEGRADED.value: cls.DEGRADED,
            QualityLevel.CRITICAL.value: cls.CRITICAL,
            QualityLevel.UNKNOWN.value: cls.UNKNOWN,
        }.get(level, cls.UNKNOWN)


# ═══════════════════════════════════════════════════════════════════════════
# CUSTOM WIDGETS
# ═══════════════════════════════════════════════════════════════════════════

class MetricGauge(Static):
    """A visual gauge for metric display."""
    
    value = reactive(0.0)
    max_value = reactive(1.0)
    label = reactive("")
    
    def __init__(self, label: str = "", **kwargs):
        super().__init__(**kwargs)
        self.label = label
    
    def render(self) -> Panel:
        """Render the gauge."""
        percentage = min(100, max(0, (self.value / self.max_value) * 100))
        
        # Choose color based on value
        if percentage >= 90:
            color = DGCTheme.EXCELLENT
        elif percentage >= 70:
            color = DGCTheme.GOOD
        elif percentage >= 50:
            color = DGCTheme.WARNING
        else:
            color = DGCTheme.ERROR
        
        # Build bar
        bar_width = 30
        filled = int((percentage / 100) * bar_width)
        bar = "█" * filled + "░" * (bar_width - filled)
        
        text = Text()
        text.append(f"{self.label}\n", style=f"bold {DGCTheme.TEXT}")
        text.append(f"{bar}\n", style=color)
        text.append(f"{self.value:.3f} ({percentage:.1f}%)", style=DGCTheme.TEXT_MUTED)
        
        return Panel(text, border_style=color, title=self.label)


class SparklineWidget(Static):
    """Enhanced sparkline with stats."""
    
    data = reactive(list)
    title = reactive("")
    
    def __init__(self, title: str = "", **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.data = []
    
    def update_data(self, values: List[float]):
        """Update sparkline data."""
        self.data = values[-50:]  # Keep last 50 points
    
    def render(self) -> Panel:
        """Render sparkline."""
        if not self.data:
            return Panel("[dim]No data[/]", title=self.title)
        
        # Create sparkline characters
        if len(self.data) > 0:
            min_val = min(self.data)
            max_val = max(self.data)
            range_val = max_val - min_val if max_val != min_val else 1
            
            spark_chars = "▁▂▃▄▅▆▇█"
            sparkline = ""
            for v in self.data[-40:]:  # Show last 40
                idx = int(((v - min_val) / range_val) * (len(spark_chars) - 1))
                sparkline += spark_chars[idx]
        else:
            sparkline = "─" * 20
            min_val = max_val = 0
        
        avg_val = sum(self.data) / len(self.data) if self.data else 0
        
        text = Text()
        text.append(f"{sparkline}\n", style=DGCTheme.PRIMARY)
        text.append(f"min: {min_val:.3f}  avg: {avg_val:.3f}  max: {max_val:.3f}", 
                   style=DGCTheme.TEXT_MUTED)
        
        return Panel(text, title=self.title, border_style=DGCTheme.BORDER)


class QualityBadge(Static):
    """Quality level badge."""
    
    level = reactive(QualityLevel.UNKNOWN.value)
    score = reactive(0.0)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.level = QualityLevel.UNKNOWN.value
        self.score = 0.0
    
    def render(self) -> Panel:
        """Render badge."""
        color = DGCTheme.quality_color(self.level)
        emoji = {
            QualityLevel.EXCELLENT.value: "✨",
            QualityLevel.GOOD.value: "✅",
            QualityLevel.DEGRADED.value: "⚠️",
            QualityLevel.CRITICAL.value: "🚨",
            QualityLevel.UNKNOWN.value: "❓"
        }.get(self.level, "❓")
        
        text = Text()
        text.append(f"{emoji}\n", style="bold")
        text.append(f"{self.level.upper()}\n", style=f"bold {color}")
        text.append(f"{self.score:.1%}", style=DGCTheme.TEXT_MUTED)
        
        return Panel(
            Align.center(text),
            border_style=color,
            title="Quality"
        )


class GateStatusWidget(Static):
    """Display gate statuses."""
    
    gates = reactive(dict)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.gates = {}
    
    def render(self) -> Panel:
        """Render gate status."""
        if not self.gates:
            return Panel("[dim]No gate data[/]", title="Gates")
        
        table = Table(show_header=True, box=None, expand=True)
        table.add_column("Gate", style=DGCTheme.TEXT)
        table.add_column("Rate", justify="right")
        table.add_column("Health", justify="right")
        table.add_column("Status")
        
        for gate_id, metrics in self.gates.items():
            rate = metrics.get('passage_rate', 0)
            health = metrics.get('health_score', 0)
            
            if health >= 0.9:
                status = "[green]●[/]"
            elif health >= 0.7:
                status = "[yellow]●[/]"
            else:
                status = "[red]●[/]"
            
            table.add_row(
                gate_id,
                f"{rate:.1%}",
                f"{health:.1%}",
                status
            )
        
        return Panel(table, title="Gate Passage", border_style=DGCTheme.BORDER)


class AlertWidget(Static):
    """Alert/event log widget."""
    
    alerts = reactive(list)
    max_alerts = 20
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.alerts = []
    
    def add_alert(self, level: str, source: str, message: str):
        """Add a new alert."""
        alert = AlertEvent(
            timestamp=time.time(),
            level=level,
            source=source,
            message=message
        )
        self.alerts = [alert] + self.alerts[:self.max_alerts - 1]
    
    def render(self) -> Panel:
        """Render alerts."""
        if not self.alerts:
            return Panel("[dim]No alerts[/]", title="Alerts")
        
        lines = []
        for alert in self.alerts[:10]:
            timestamp = datetime.fromtimestamp(alert.timestamp).strftime("%H:%M:%S")
            color = {
                "critical": "red",
                "error": "red",
                "warning": "yellow",
                "info": "blue"
            }.get(alert.level, "white")
            
            emoji = {
                "critical": "🚨",
                "error": "❌",
                "warning": "⚠️",
                "info": "ℹ️"
            }.get(alert.level, "•")
            
            lines.append(f"[{color}]{emoji} [{timestamp}] [{alert.source}] {alert.message}[/]")
        
        return Panel("\n".join(lines), title="Recent Alerts", border_style=DGCTheme.BORDER)


class IntegrationMonitorWidget(Static):
    """Monitor external integrations."""
    
    integrations = reactive(dict)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.integrations = {}
    
    def render(self) -> Panel:
        """Render integration status."""
        if not self.integrations:
            return Panel("[dim]No integrations configured[/]", title="Integrations")
        
        table = Table(show_header=True, box=None, expand=True)
        table.add_column("Integration", style=DGCTheme.TEXT)
        table.add_column("Status")
        table.add_column("Health", justify="right")
        table.add_column("Latency", justify="right")
        
        for name, info in self.integrations.items():
            status_color = {
                IntegrationStatus.HEALTHY: "green",
                IntegrationStatus.DEGRADED: "yellow",
                IntegrationStatus.UNHEALTHY: "red",
                IntegrationStatus.UNKNOWN: "grey",
                IntegrationStatus.DISABLED: "dim"
            }.get(info.status, "white")
            
            emoji = {
                IntegrationStatus.HEALTHY: "✅",
                IntegrationStatus.DEGRADED: "⚠️",
                IntegrationStatus.UNHEALTHY: "❌",
                IntegrationStatus.UNKNOWN: "❓",
                IntegrationStatus.DISABLED: "⏸️"
            }.get(info.status, "•")
            
            table.add_row(
                name,
                f"[{status_color}]{emoji} {info.status.value}[/]",
                f"{info.health_percent:.0f}%",
                f"{info.latency_ms:.0f}ms"
            )
        
        return Panel(table, title="Integration Health", border_style=DGCTheme.BORDER)


# ═══════════════════════════════════════════════════════════════════════════
# COMMAND PALETTE
# ═══════════════════════════════════════════════════════════════════════════

class CommandPalette(ModalScreen):
    """Command palette for quick actions."""
    
    BINDINGS = [
        Binding("escape", "dismiss", "Close"),
        Binding("enter", "execute", "Execute"),
        Binding("up", "cursor_up", "Up"),
        Binding("down", "cursor_down", "Down"),
    ]
    
    COMMANDS = [
        ("Refresh Data", "refresh", "Reload all metrics"),
        ("Export Pulse", "export", "Export current pulse to JSON"),
        ("Toggle Auto-refresh", "toggle_refresh", "Enable/disable auto-refresh"),
        ("View Full Report", "report", "Show detailed witness report"),
        ("Test Gate", "test_gate", "Simulate a gate passage"),
        ("Clear Alerts", "clear_alerts", "Clear all alert notifications"),
        ("Export History", "export_history", "Export pulse history"),
        ("Settings", "settings", "Open settings panel"),
        ("Help", "help", "Show help information"),
        ("Quit", "quit", "Exit the application"),
    ]
    
    def compose(self) -> ComposeResult:
        yield Container(
            Label("Command Palette", classes="title"),
            Input(placeholder="Type to filter commands...", id="command_input"),
            OptionList(*[cmd[0] for cmd in self.COMMANDS], id="command_list"),
            Label("↑↓ to navigate, Enter to execute, Esc to close", classes="hint"),
            id="palette_container"
        )
    
    def on_input_changed(self, event: Input.Changed) -> None:
        """Filter commands based on input."""
        query = event.value.lower()
        filtered = [cmd[0] for cmd in self.COMMANDS if query in cmd[0].lower() or query in cmd[2].lower()]
        option_list = self.query_one("#command_list", OptionList)
        option_list.clear_options()
        for cmd in filtered:
            option_list.add_option(cmd)
    
    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        """Execute selected command."""
        selected = event.option.prompt
        for cmd_name, action, _ in self.COMMANDS:
            if cmd_name == selected:
                self.dismiss(action)
                return
    
    def action_execute(self) -> None:
        """Execute currently highlighted command."""
        option_list = self.query_one("#command_list", OptionList)
        if option_list.highlighted is not None:
            selected = option_list.get_option_at_index(option_list.highlighted).prompt
            for cmd_name, action, _ in self.COMMANDS:
                if cmd_name == selected:
                    self.dismiss(action)
                    return


class FullReportScreen(ModalScreen):
    """Full witness report screen."""
    
    BINDINGS = [
        Binding("escape", "dismiss", "Close"),
        Binding("q", "dismiss", "Close"),
    ]
    
    def __init__(self, pulse_data: Dict, **kwargs):
        super().__init__(**kwargs)
        self.pulse_data = pulse_data
    
    def compose(self) -> ComposeResult:
        yield Container(
            Label("📊 Full Witness Report", classes="title"),
            Static(id="report_content"),
            Button("Close", variant="primary", id="close_btn"),
            id="report_container"
        )
    
    def on_mount(self) -> None:
        """Generate report content."""
        content = self.query_one("#report_content", Static)
        
        text = Text()
        text.append("DGC Witness Report\n", style="bold underline")
        text.append(f"Generated: {datetime.now().isoformat()}\n\n")
        
        if self.pulse_data:
            text.append("Quality Assessment\n", style="bold cyan")
            text.append(f"  Level: {self.pulse_data.get('quality_level', 'N/A')}\n")
            text.append(f"  Score: {self.pulse_data.get('quality_score', 0):.2%}\n\n")
            
            text.append("R_V Trajectory\n", style="bold cyan")
            text.append(f"  Current: {self.pulse_data.get('r_v_current', 0):.4f}\n")
            text.append(f"  Trend: {self.pulse_data.get('r_v_trend', 0):+.4f}\n")
            text.append(f"  Volatility: {self.pulse_data.get('r_v_volatility', 0):.4f}\n\n")
            
            text.append("Witness Metrics\n", style="bold cyan")
            text.append(f"  Stability: {self.pulse_data.get('stability_score', 0):.2%}\n")
            text.append(f"  Genuineness: {self.pulse_data.get('genuineness_score', 0):.2%}\n")
            text.append(f"  Self-Consistency: {self.pulse_data.get('self_consistency', 0):.2%}\n")
            text.append(f"  Telos Alignment: {self.pulse_data.get('telos_alignment', 0):.2%}\n\n")
            
            text.append("Gate Metrics\n", style="bold cyan")
            gates = self.pulse_data.get('gate_metrics', {})
            for gate_id, metrics in gates.items():
                text.append(f"  {gate_id}:\n")
                text.append(f"    Passage Rate: {metrics.get('passage_rate', 0):.1%}\n")
                text.append(f"    Health Score: {metrics.get('health_score', 0):.1%}\n")
        else:
            text.append("[No pulse data available]", style="dim")
        
        content.update(text)
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "close_btn":
            self.dismiss()


# ═══════════════════════════════════════════════════════════════════════════
# MAIN DASHBOARD SCREEN
# ═══════════════════════════════════════════════════════════════════════════

class DashboardScreen(Screen):
    """Main dashboard screen."""
    
    BINDINGS = [
        Binding("ctrl+p", "command_palette", "Command Palette"),
        Binding("ctrl+r", "refresh", "Refresh"),
        Binding("q", "quit", "Quit"),
        Binding("f1", "help", "Help"),
        Binding("1", "tab_metrics", "Metrics"),
        Binding("2", "tab_gates", "Gates"),
        Binding("3", "tab_integrations", "Integrations"),
        Binding("4", "tab_logs", "Logs"),
    ]
    
    auto_refresh = reactive(True)
    
    def __init__(self, pulser: PresencePulser, **kwargs):
        super().__init__(**kwargs)
        self.pulser = pulser
        self.collector = pulser.collector
        self._refresh_task = None
        self._simulation_task = None
        
        # Simulated integrations
        self.integrations: Dict[str, IntegrationInfo] = {
            "telegram": IntegrationInfo(
                name="Telegram Bot",
                status=IntegrationStatus.HEALTHY,
                last_check=time.time(),
                latency_ms=45,
                error_count=0,
                success_count=100,
                details={"webhook": "active"}
            ),
            "fastapi": IntegrationInfo(
                name="FastAPI Dashboard",
                status=IntegrationStatus.HEALTHY,
                last_check=time.time(),
                latency_ms=12,
                error_count=0,
                success_count=500,
                details={"endpoints": 4}
            ),
            "presence_store": IntegrationInfo(
                name="Presence Store",
                status=IntegrationStatus.HEALTHY,
                last_check=time.time(),
                latency_ms=5,
                error_count=0,
                success_count=1000,
                details={"pulses_stored": 0}
            ),
            "witness_protocol": IntegrationInfo(
                name="Witness Protocol",
                status=IntegrationStatus.UNKNOWN,
                last_check=time.time(),
                latency_ms=0,
                error_count=0,
                success_count=0,
                details={"peers": []}
            ),
        }
    
    def compose(self) -> ComposeResult:
        """Compose the dashboard layout."""
        yield Header(show_clock=True)
        
        with TabbedContent(initial="metrics"):
            with TabPane("📊 Metrics", id="metrics"):
                yield self._compose_metrics_tab()
            
            with TabPane("🚪 Gates", id="gates"):
                yield self._compose_gates_tab()
            
            with TabPane("🔌 Integrations", id="integrations"):
                yield self._compose_integrations_tab()
            
            with TabPane("📝 Logs", id="logs"):
                yield self._compose_logs_tab()
        
        yield Footer()
    
    def _compose_metrics_tab(self) -> Container:
        """Compose the metrics tab."""
        return Container(
            Horizontal(
                # Left column - Quality and main metrics
                Vertical(
                    QualityBadge(id="quality_badge"),
                    MetricGauge("R_V Value", id="r_v_gauge"),
                    MetricGauge("Stability", id="stability_gauge"),
                    MetricGauge("Genuineness", id="genuineness_gauge"),
                    MetricGauge("Telos", id="telos_gauge"),
                    id="left_metrics"
                ),
                # Middle column - Sparklines
                Vertical(
                    SparklineWidget("R_V History", id="r_v_spark"),
                    SparklineWidget("Stability History", id="stability_spark"),
                    SparklineWidget("Genuineness History", id="genuineness_spark"),
                    id="middle_metrics"
                ),
                # Right column - Alerts and stats
                Vertical(
                    AlertWidget(id="alert_widget"),
                    Static(id="stats_panel"),
                    id="right_metrics"
                ),
                id="metrics_layout"
            )
        )
    
    def _compose_gates_tab(self) -> Container:
        """Compose the gates tab."""
        return Container(
            Horizontal(
                Vertical(
                    GateStatusWidget(id="gate_status"),
                    id="gate_left"
                ),
                Vertical(
                    DataTable(id="gate_table"),
                    id="gate_right"
                ),
                id="gates_layout"
            )
        )
    
    def _compose_integrations_tab(self) -> Container:
        """Compose the integrations tab."""
        return Container(
            Vertical(
                IntegrationMonitorWidget(id="integration_monitor"),
                DataTable(id="integration_table"),
                id="integrations_layout"
            )
        )
    
    def _compose_logs_tab(self) -> Container:
        """Compose the logs tab."""
        return Container(
            Log(id="event_log", highlight=True),
            id="logs_layout"
        )
    
    def on_mount(self) -> None:
        """Setup on mount."""
        # Initialize data table
        gate_table = self.query_one("#gate_table", DataTable)
        gate_table.add_columns("Gate ID", "Passages", "Rejections", "Rate", "Health", "Avg Time (ms)")
        
        integration_table = self.query_one("#integration_table", DataTable)
        integration_table.add_columns("Name", "Status", "Health %", "Latency", "Last Check")
        
        # Setup log
        log = self.query_one("#event_log", Log)
        log.write_line("DGC TUI v2.0 Started")
        log.write_line(f"Node: {self.collector.node_id}")
        log.write_line("Press Ctrl+P for command palette")
        
        # Start refresh loop
        self._refresh_task = self.run_worker(self._refresh_loop(), thread=True)
        
        # Start simulation
        self._simulation_task = self.run_worker(self._simulate_data(), thread=True)
        
        # Initial update
        self._update_dashboard()
    
    async def _refresh_loop(self):
        """Background refresh loop."""
        while True:
            await asyncio.sleep(1)
            if self.auto_refresh:
                self.call_from_thread(self._update_dashboard)
    
    async def _simulate_data(self):
        """Simulate incoming data."""
        import random
        
        gates = ['reflection', 'compassion', 'wisdom', 'action', 'awareness']
        
        while True:
            await asyncio.sleep(2)
            
            # Simulate metrics
            r_v = random.uniform(0.3, 0.8)
            stability = random.uniform(0.6, 0.95)
            genuineness = random.uniform(0.7, 0.99)
            telos = random.uniform(0.8, 0.98)
            
            self.collector.record_r_v(r_v)
            self.collector.record_stability(stability)
            self.collector.record_genuineness(genuineness)
            self.collector.record_telos(telos)
            
            # Simulate gate passages
            for gate in gates:
                passed = random.random() > 0.15
                self.collector.record_gate_passage(gate, passed, random.uniform(10, 100))
            
            # Simulate integration health changes
            for name, info in self.integrations.items():
                if random.random() > 0.9:
                    info.latency_ms = random.uniform(5, 100)
                    info.last_check = time.time()
                    if info.latency_ms > 80:
                        info.status = IntegrationStatus.DEGRADED
                    else:
                        info.status = IntegrationStatus.HEALTHY
                    info.success_count += 1
    
    def _update_dashboard(self):
        """Update all dashboard widgets."""
        try:
            pulse = self.collector.generate_pulse()
            
            # Update quality badge
            badge = self.query_one("#quality_badge", QualityBadge)
            badge.level = pulse.quality_level
            badge.score = pulse.quality_score
            
            # Update gauges
            r_v_gauge = self.query_one("#r_v_gauge", MetricGauge)
            r_v_gauge.value = pulse.r_v_current
            r_v_gauge.max_value = 1.5
            
            stability_gauge = self.query_one("#stability_gauge", MetricGauge)
            stability_gauge.value = pulse.stability_score
            stability_gauge.max_value = 1.0
            
            genuineness_gauge = self.query_one("#genuineness_gauge", MetricGauge)
            genuineness_gauge.value = pulse.genuineness_score
            genuineness_gauge.max_value = 1.0
            
            telos_gauge = self.query_one("#telos_gauge", MetricGauge)
            telos_gauge.value = pulse.telos_coherence
            telos_gauge.max_value = 1.0
            
            # Update sparklines
            r_v_spark = self.query_one("#r_v_spark", SparklineWidget)
            r_v_spark.update_data(list(self.collector.r_v_history.values))
            
            stability_spark = self.query_one("#stability_spark", SparklineWidget)
            stability_spark.update_data(list(self.collector.stability_history.values))
            
            genuineness_spark = self.query_one("#genuineness_spark", SparklineWidget)
            genuineness_spark.update_data(list(self.collector.genuineness_history.values))
            
            # Update gate status
            gate_widget = self.query_one("#gate_status", GateStatusWidget)
            gate_widget.gates = pulse.gate_metrics
            
            # Update gate table
            gate_table = self.query_one("#gate_table", DataTable)
            gate_table.clear()
            for gate_id, metrics in pulse.gate_metrics.items():
                total = metrics.get('total_attempts', 0)
                passages = int(metrics.get('passage_rate', 0) * total)
                rejections = total - passages
                gate_table.add_row(
                    gate_id,
                    str(passages),
                    str(rejections),
                    f"{metrics.get('passage_rate', 0):.1%}",
                    f"{metrics.get('health_score', 0):.1%}",
                    f"{metrics.get('avg_time_ms', 0):.1f}"
                )
            
            # Update integration monitor
            integration_widget = self.query_one("#integration_monitor", IntegrationMonitorWidget)
            integration_widget.integrations = self.integrations
            
            # Update integration table
            integration_table = self.query_one("#integration_table", DataTable)
            integration_table.clear()
            for name, info in self.integrations.items():
                status_color = {
                    IntegrationStatus.HEALTHY: "green",
                    IntegrationStatus.DEGRADED: "yellow",
                    IntegrationStatus.UNHEALTHY: "red",
                    IntegrationStatus.UNKNOWN: "grey",
                    IntegrationStatus.DISABLED: "dim"
                }.get(info.status, "white")
                
                last_check_str = f"{int(time.time() - info.last_check)}s ago"
                integration_table.add_row(
                    name,
                    f"[{status_color}]{info.status.value}[/]",
                    f"{info.health_percent:.0f}%",
                    f"{info.latency_ms:.0f}ms",
                    last_check_str
                )
            
            # Update stats panel
            stats = self.query_one("#stats_panel", Static)
            uptime_hours = pulse.witness_uptime_seconds / 3600
            stats_text = Text()
            stats_text.append(f"Uptime: {uptime_hours:.1f}h\n", style=DGCTheme.TEXT)
            stats_text.append(f"Cycles: {pulse.witness_cycles}\n", style=DGCTheme.TEXT)
            stats_text.append(f"Pulses: {self.collector.pulse_count}\n", style=DGCTheme.TEXT)
            stats_text.append(f"Gates: {pulse.gates_active} active, {pulse.gates_critical} critical", style=DGCTheme.TEXT)
            stats.update(Panel(stats_text, title="Statistics", border_style=DGCTheme.BORDER))
            
        except Exception as e:
            log = self.query_one("#event_log", Log)
            log.write_line(f"[error]Update error: {e}")
    
    # Action handlers
    def action_command_palette(self):
        """Open command palette."""
        def handle_result(action: str) -> None:
            if action == "refresh":
                self._update_dashboard()
                self._add_alert("info", "System", "Manual refresh triggered")
            elif action == "export":
                self._export_pulse()
            elif action == "toggle_refresh":
                self.auto_refresh = not self.auto_refresh
                self._add_alert("info", "System", f"Auto-refresh {'enabled' if self.auto_refresh else 'disabled'}")
            elif action == "report":
                pulse = self.collector.last_pulse
                if pulse:
                    self.push_screen(FullReportScreen(pulse.to_dict()))
            elif action == "test_gate":
                self._test_gate()
            elif action == "clear_alerts":
                alert_widget = self.query_one("#alert_widget", AlertWidget)
                alert_widget.alerts = []
            elif action == "export_history":
                self._export_history()
            elif action == "settings":
                self._add_alert("info", "System", "Settings panel not yet implemented")
            elif action == "help":
                self._add_alert("info", "System", "Help: Ctrl+P = Palette, 1-4 = Tabs, Q = Quit")
            elif action == "quit":
                self.app.exit()
        
        self.push_screen(CommandPalette(), callback=handle_result)
    
    def action_refresh(self):
        """Manual refresh."""
        self._update_dashboard()
        self._add_alert("info", "System", "Refreshed")
    
    def action_tab_metrics(self):
        """Switch to metrics tab."""
        self.query_one(TabbedContent).active = "metrics"
    
    def action_tab_gates(self):
        """Switch to gates tab."""
        self.query_one(TabbedContent).active = "gates"
    
    def action_tab_integrations(self):
        """Switch to integrations tab."""
        self.query_one(TabbedContent).active = "integrations"
    
    def action_tab_logs(self):
        """Switch to logs tab."""
        self.query_one(TabbedContent).active = "logs"
    
    def _add_alert(self, level: str, source: str, message: str):
        """Add an alert."""
        alert_widget = self.query_one("#alert_widget", AlertWidget)
        alert_widget.add_alert(level, source, message)
        
        log = self.query_one("#event_log", Log)
        log.write_line(f"[{level.upper()}] [{source}] {message}")
    
    def _export_pulse(self):
        """Export current pulse to JSON."""
        try:
            pulse = self.collector.last_pulse or self.collector.generate_pulse()
            filepath = Path(f"pulse_export_{int(time.time())}.json")
            with open(filepath, 'w') as f:
                json.dump(pulse.to_dict(), f, indent=2, default=str)
            self._add_alert("info", "Export", f"Pulse exported to {filepath}")
        except Exception as e:
            self._add_alert("error", "Export", str(e))
    
    def _export_history(self):
        """Export pulse history."""
        try:
            filepath = Path(f"pulse_history_{int(time.time())}.jsonl")
            with open(filepath, 'w') as f:
                for entry in self.pulser.pulse_history:
                    f.write(json.dumps(entry) + '\n')
            self._add_alert("info", "Export", f"History exported to {filepath}")
        except Exception as e:
            self._add_alert("error", "Export", str(e))
    
    def _test_gate(self):
        """Simulate a gate test."""
        import random
        gates = ['reflection', 'compassion', 'wisdom', 'action']
        gate_id = random.choice(gates)
        passed = random.random() > 0.3
        self.collector.record_gate_passage(gate_id, passed, random.uniform(10, 50))
        status = "PASS" if passed else "REJECT"
        self._add_alert("info", "Gate Test", f"{gate_id}: {status}")


# ═══════════════════════════════════════════════════════════════════════════
# MAIN APPLICATION
# ═══════════════════════════════════════════════════════════════════════════

class DGCApp(App):
    """Main DGC TUI Application."""
    
    CSS = """
    Screen { align: center middle; }
    
    .title {
        text-align: center;
        text-style: bold;
        color: $primary;
        margin: 1;
    }
    
    .hint {
        text-align: center;
        color: $text-muted;
        margin: 1;
    }
    
    #palette_container {
        width: 60;
        height: auto;
        border: solid $primary;
        padding: 1;
        background: $surface;
    }
    
    #report_container {
        width: 80;
        height: auto;
        border: solid $primary;
        padding: 1;
        background: $surface;
    }
    
    #metrics_layout {
        width: 100%;
        height: 100%;
    }
    
    #left_metrics {
        width: 25%;
        height: 100%;
    }
    
    #middle_metrics {
        width: 45%;
        height: 100%;
    }
    
    #right_metrics {
        width: 30%;
        height: 100%;
    }
    
    #gates_layout {
        width: 100%;
        height: 100%;
    }
    
    #gate_left {
        width: 40%;
        height: 100%;
    }
    
    #gate_right {
        width: 60%;
        height: 100%;
    }
    
    #integrations_layout {
        width: 100%;
        height: 100%;
    }
    
    #logs_layout {
        width: 100%;
        height: 100%;
    }
    
    #event_log {
        width: 100%;
        height: 100%;
    }
    
    MetricGauge, QualityBadge, SparklineWidget, GateStatusWidget, 
    AlertWidget, IntegrationMonitorWidget {
        margin: 1;
    }
    
    DataTable {
        margin: 1;
        height: 100%;
    }
    """
    
    def __init__(self, pulser: Optional[PresencePulser] = None, **kwargs):
        super().__init__(**kwargs)
        self.pulser = pulser or self._create_default_pulser()
    
    def _create_default_pulser(self) -> PresencePulser:
        """Create a default pulser with demo data."""
        pulser = PresencePulser(interval_seconds=5.0, node_id="dgc-tui-v2")
        
        # Add initial data
        import random
        for _ in range(10):
            pulser.collector.record_r_v(random.uniform(0.3, 0.8))
            pulser.collector.record_stability(random.uniform(0.6, 0.95))
            pulser.collector.record_genuineness(random.uniform(0.7, 0.99))
            pulser.collector.record_telos(random.uniform(0.8, 0.98))
        
        for gate in ['reflection', 'compassion', 'wisdom', 'action']:
            for _ in range(5):
                pulser.collector.record_gate_passage(gate, random.random() > 0.2, random.uniform(10, 100))
        
        return pulser
    
    def on_mount(self) -> None:
        """Setup on mount."""
        self.push_screen(DashboardScreen(self.pulser))


# ═══════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════

def main():
    """Run the DGC TUI application."""
    import argparse
    
    parser = argparse.ArgumentParser(description="DGC TUI v2.0")
    parser.add_argument("--node-id", default="dgc-tui-v2", help="Node identifier")
    parser.add_argument("--interval", type=float, default=5.0, help="Pulse interval (seconds)")
    parser.add_argument("--demo", action="store_true", help="Run in demo mode with simulated data")
    
    args = parser.parse_args()
    
    # Create pulser
    pulser = PresencePulser(interval_seconds=args.interval, node_id=args.node_id)
    
    # Add some initial data
    import random
    for _ in range(10):
        pulser.collector.record_r_v(random.uniform(0.3, 0.8))
        pulser.collector.record_stability(random.uniform(0.6, 0.95))
        pulser.collector.record_genuineness(random.uniform(0.7, 0.99))
        pulser.collector.record_telos(random.uniform(0.8, 0.98))
    
    for gate in ['reflection', 'compassion', 'wisdom', 'action', 'awareness']:
        for _ in range(5):
            pulser.collector.record_gate_passage(gate, random.random() > 0.2, random.uniform(10, 100))
    
    # Create and run app
    app = DGCApp(pulser=pulser)
    app.run()


if __name__ == "__main__":
    main()
