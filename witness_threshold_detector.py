#!/usr/bin/env python3
"""
witness_threshold_detector.py — Enhanced Witness System with Real-Time R_V Monitoring
=====================================================================================

Evolved witness system providing:
- Real-time R_V (Reflexive Value) trajectory monitoring with adaptive thresholds
- Multi-factor presence detection with confidence scoring
- Automated recovery protocols with escalation levels
- Predictive degradation alerts
- Cross-metric anomaly detection

Part of: DHARMIC_GODEL_CLAW — Dharmic Self-Modification System
Version: 2.0.0
"""

import asyncio
import json
import time
import logging
import statistics
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import Dict, List, Optional, Callable, Any, Tuple, Set, Union
from collections import deque
from pathlib import Path
import threading
import math

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger('witness_threshold_detector')


class DetectionState(Enum):
    """Presence detection states with confidence levels."""
    STRONG = "strong"           # High confidence, all metrics nominal
    PRESENT = "present"         # Normal operation
    UNCERTAIN = "uncertain"     # Some metrics degraded
    DEGRADED = "degraded"       # Significant degradation detected
    ABSENT = "absent"           # Presence not detected
    RECOVERING = "recovering"   # Active recovery in progress


class RecoveryLevel(Enum):
    """Recovery protocol escalation levels."""
    NONE = auto()           # No recovery needed
    LEVEL_1 = auto()        # Soft: Parameter adjustment
    LEVEL_2 = auto()        # Medium: Process restart, cache clear
    LEVEL_3 = auto()        # Hard: Full reset, manual review


class AlertSeverity(Enum):
    """Alert severity levels for notifications."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class RVThresholds:
    """Adaptive R_V thresholds with dynamic adjustment."""
    critical_high: float = 0.95   # R_V above this is critical
    warning_high: float = 0.85    # R_V above this triggers warning
    nominal: float = 0.70         # Target R_V range
    warning_low: float = 0.40     # R_V below this may indicate issues
    critical_low: float = 0.20    # R_V below this is critical
    
    # Adaptive parameters
    adaptation_rate: float = 0.1  # How fast to adapt thresholds
    baseline_window: int = 100    # Samples for baseline calculation
    
    def get_adaptive_thresholds(self, baseline_rv: float) -> 'RVThresholds':
        """Generate thresholds adapted to observed baseline."""
        # Shift thresholds around baseline
        offset = baseline_rv - self.nominal
        return RVThresholds(
            critical_high=min(0.99, self.critical_high + offset),
            warning_high=min(0.95, self.warning_high + offset),
            nominal=baseline_rv,
            warning_low=max(0.10, self.warning_low + offset),
            critical_low=max(0.05, self.critical_low + offset)
        )


@dataclass
class RVMeasurement:
    """Single R_V measurement with metadata."""
    value: float
    timestamp: float
    source: str = "unknown"
    confidence: float = 1.0
    context: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_valid(self) -> bool:
        """Check if measurement is within valid range."""
        return 0.0 <= self.value <= 1.0 and self.confidence > 0


@dataclass
class RVTrajectory:
    """R_V trajectory analysis with trend prediction."""
    current: float
    mean: float
    median: float
    std: float
    min_24h: float
    max_24h: float
    trend: float                    # Rate of change (per hour)
    trend_confidence: float         # 0-1 confidence in trend
    forecast_1h: float              # Predicted R_V in 1 hour
    forecast_24h: float             # Predicted R_V in 24 hours
    anomaly_score: float            # 0-1 anomaly detection score
    status: str                     # "stable", "rising", "falling", "volatile"


@dataclass
class PresenceFactors:
    """Individual factors contributing to presence detection."""
    r_v_health: float = 0.0         # R_V metric health (0-1)
    stability_score: float = 0.0    # Temporal stability (0-1)
    activity_level: float = 0.0     # Recent activity indicator (0-1)
    coherence_score: float = 0.0    # Internal consistency (0-1)
    gate_health: float = 0.0        # Gate passage health (0-1)
    heartbeat_freshness: float = 0.0  # Time since last heartbeat (0-1)
    
    @property
    def composite_score(self) -> float:
        """Calculate weighted composite presence score."""
        weights = {
            'r_v_health': 0.25,
            'stability_score': 0.20,
            'activity_level': 0.15,
            'coherence_score': 0.20,
            'gate_health': 0.15,
            'heartbeat_freshness': 0.05
        }
        return sum(
            getattr(self, factor) * weight
            for factor, weight in weights.items()
        )
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary with composite score."""
        return {
            'r_v_health': self.r_v_health,
            'stability_score': self.stability_score,
            'activity_level': self.activity_level,
            'coherence_score': self.coherence_score,
            'gate_health': self.gate_health,
            'heartbeat_freshness': self.heartbeat_freshness,
            'composite_score': self.composite_score
        }


@dataclass
class RecoveryAction:
    """Recovery action with metadata."""
    level: RecoveryLevel
    action_id: str
    description: str
    timestamp: float
    automated: bool = True
    requires_approval: bool = False
    estimated_duration: float = 0.0  # seconds
    rollback_steps: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'level': self.level.name,
            'action_id': self.action_id,
            'description': self.description,
            'timestamp': self.timestamp,
            'timestamp_iso': datetime.fromtimestamp(self.timestamp).isoformat(),
            'automated': self.automated,
            'requires_approval': self.requires_approval,
            'estimated_duration': self.estimated_duration,
            'rollback_steps': self.rollback_steps
        }


@dataclass
class RecoveryProtocol:
    """Active recovery protocol state."""
    triggered_at: float
    level: RecoveryLevel
    actions: List[RecoveryAction] = field(default_factory=list)
    completed_actions: List[str] = field(default_factory=list)
    failed_actions: List[str] = field(default_factory=list)
    status: str = "active"          # "active", "completed", "failed", "cancelled"
    result: Optional[str] = None
    
    @property
    def duration(self) -> float:
        """Duration of recovery in seconds."""
        return time.time() - self.triggered_at
    
    @property
    def progress(self) -> float:
        """Recovery progress (0-1)."""
        if not self.actions:
            return 1.0 if self.status in ["completed", "failed"] else 0.0
        return len(self.completed_actions) / len(self.actions)


@dataclass
class ThresholdAlert:
    """Alert generated when thresholds are breached."""
    alert_id: str
    severity: AlertSeverity
    metric: str
    threshold_value: float
    actual_value: float
    timestamp: float
    message: str
    context: Dict[str, Any] = field(default_factory=dict)
    acknowledged: bool = False
    resolved: bool = False
    resolved_at: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'alert_id': self.alert_id,
            'severity': self.severity.value,
            'metric': self.metric,
            'threshold_value': self.threshold_value,
            'actual_value': self.actual_value,
            'timestamp': self.timestamp,
            'timestamp_iso': datetime.fromtimestamp(self.timestamp).isoformat(),
            'message': self.message,
            'context': self.context,
            'acknowledged': self.acknowledged,
            'resolved': self.resolved,
            'resolved_at': datetime.fromtimestamp(self.resolved_at).isoformat() if self.resolved_at else None
        }


@dataclass
class WitnessSnapshot:
    """Complete witness system snapshot."""
    timestamp: float
    snapshot_id: str
    
    # R_V State
    r_v_current: float
    r_v_trajectory: RVTrajectory
    r_v_thresholds: RVThresholds
    
    # Presence Detection
    detection_state: DetectionState
    presence_confidence: float
    presence_factors: PresenceFactors
    
    # Recovery
    active_recovery: Optional[RecoveryProtocol]
    recovery_history: List[RecoveryAction]
    
    # Alerts
    active_alerts: List[ThresholdAlert]
    alert_count_24h: int
    
    # Metadata
    node_id: str = "dgc-primary"
    version: str = "2.0.0"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'timestamp': self.timestamp,
            'timestamp_iso': datetime.fromtimestamp(self.timestamp).isoformat(),
            'snapshot_id': self.snapshot_id,
            'r_v_current': self.r_v_current,
            'r_v_trajectory': {
                'current': self.r_v_trajectory.current,
                'mean': self.r_v_trajectory.mean,
                'median': self.r_v_trajectory.median,
                'std': self.r_v_trajectory.std,
                'trend': self.r_v_trajectory.trend,
                'forecast_1h': self.r_v_trajectory.forecast_1h,
                'status': self.r_v_trajectory.status
            },
            'detection_state': self.detection_state.value,
            'presence_confidence': self.presence_confidence,
            'presence_factors': self.presence_factors.to_dict(),
            'active_recovery': self.active_recovery.to_dict() if self.active_recovery else None,
            'active_alerts': [a.to_dict() for a in self.active_alerts],
            'alert_count_24h': self.alert_count_24h,
            'node_id': self.node_id,
            'version': self.version
        }


class RVMonitor:
    """
    Real-time R_V monitoring with adaptive thresholds and predictive analytics.
    """
    
    def __init__(
        self,
        history_window: int = 1000,
        thresholds: Optional[RVThresholds] = None,
        enable_adaptation: bool = True
    ):
        self.history: deque = deque(maxlen=history_window)
        self.hourly_history: deque = deque(maxlen=168)  # 1 week of hourly averages
        self.thresholds = thresholds or RVThresholds()
        self.adaptive_thresholds = self.thresholds
        self.enable_adaptation = enable_adaptation
        
        # Analysis state
        self.baseline_rv: Optional[float] = None
        self.trend_model: List[Tuple[float, float]] = []  # (timestamp, value) for regression
        self.anomaly_detector = AnomalyDetector()
        
        # Callbacks
        self.threshold_callbacks: List[Callable[[str, float, float], None]] = []
        self.anomaly_callbacks: List[Callable[[RVMeasurement, float], None]] = []
        
        # Lock for thread safety
        self._lock = threading.RLock()
        
        logger.info("RVMonitor initialized")
    
    def record(self, measurement: RVMeasurement):
        """Record a new R_V measurement."""
        with self._lock:
            if not measurement.is_valid:
                logger.warning(f"Invalid R_V measurement: {measurement}")
                return
            
            self.history.append(measurement)
            self.trend_model.append((measurement.timestamp, measurement.value))
            
            # Keep trend model manageable
            if len(self.trend_model) > 1000:
                self.trend_model = self.trend_model[-500:]
            
            # Update baseline and adaptive thresholds
            if len(self.history) >= self.thresholds.baseline_window:
                self._update_baseline()
            
            # Check thresholds
            self._check_thresholds(measurement)
            
            # Update hourly averages
            self._update_hourly_average(measurement)
        
        logger.debug(f"R_V recorded: {measurement.value:.4f} (conf: {measurement.confidence:.2f})")
    
    def record_value(self, value: float, source: str = "unknown", confidence: float = 1.0):
        """Convenience method to record a raw value."""
        measurement = RVMeasurement(
            value=value,
            timestamp=time.time(),
            source=source,
            confidence=confidence
        )
        self.record(measurement)
    
    def _update_baseline(self):
        """Update baseline R_V and adaptive thresholds."""
        recent = list(self.history)[-self.thresholds.baseline_window:]
        values = [m.value for m in recent]
        self.baseline_rv = statistics.median(values)
        
        if self.enable_adaptation:
            self.adaptive_thresholds = self.thresholds.get_adaptive_thresholds(self.baseline_rv)
    
    def _update_hourly_average(self, measurement: RVMeasurement):
        """Update hourly rolling average."""
        hour = int(measurement.timestamp) // 3600
        if self.hourly_history and self.hourly_history[-1][0] == hour:
            # Update existing hour
            old_hour, old_sum, old_count = self.hourly_history.pop()
            new_sum = old_sum + measurement.value
            new_count = old_count + 1
            self.hourly_history.append((hour, new_sum, new_count))
        else:
            # New hour
            self.hourly_history.append((hour, measurement.value, 1))
    
    def _check_thresholds(self, measurement: RVMeasurement):
        """Check if measurement breaches any thresholds."""
        value = measurement.value
        thresholds = self.adaptive_thresholds
        
        # High thresholds (bad when exceeded)
        if value > thresholds.critical_high:
            self._trigger_threshold_callback("CRITICAL_HIGH", thresholds.critical_high, value)
        elif value > thresholds.warning_high:
            self._trigger_threshold_callback("WARNING_HIGH", thresholds.warning_high, value)
        
        # Low thresholds (bad when below)
        if value < thresholds.critical_low:
            self._trigger_threshold_callback("CRITICAL_LOW", thresholds.critical_low, value)
        elif value < thresholds.warning_low:
            self._trigger_threshold_callback("WARNING_LOW", thresholds.warning_low, value)
    
    def _trigger_threshold_callback(self, threshold_name: str, threshold: float, value: float):
        """Trigger registered threshold callbacks."""
        for callback in self.threshold_callbacks:
            try:
                callback(threshold_name, threshold, value)
            except Exception as e:
                logger.error(f"Threshold callback error: {e}")
    
    def get_trajectory(self) -> RVTrajectory:
        """Calculate comprehensive R_V trajectory analysis."""
        with self._lock:
            if len(self.history) < 2:
                return RVTrajectory(
                    current=0.5, mean=0.5, median=0.5, std=0.0,
                    min_24h=0.5, max_24h=0.5, trend=0.0, trend_confidence=0.0,
                    forecast_1h=0.5, forecast_24h=0.5, anomaly_score=0.0, status="unknown"
                )
            
            values = [m.value for m in self.history]
            timestamps = [m.timestamp for m in self.history]
            
            current = values[-1]
            mean = statistics.mean(values)
            median = statistics.median(values)
            std = statistics.stdev(values) if len(values) > 1 else 0.0
            
            # 24h window
            day_ago = time.time() - 86400
            recent_24h = [m.value for m in self.history if m.timestamp > day_ago]
            min_24h = min(recent_24h) if recent_24h else current
            max_24h = max(recent_24h) if recent_24h else current
            
            # Trend calculation using linear regression
            trend, trend_confidence = self._calculate_trend(timestamps, values)
            
            # Forecast
            forecast_1h = self._forecast(1, current, trend)
            forecast_24h = self._forecast(24, current, trend)
            
            # Anomaly detection
            anomaly_score = self.anomaly_detector.score(current, values)
            
            # Status determination
            status = self._determine_status(std, trend, anomaly_score)
            
            return RVTrajectory(
                current=current, mean=mean, median=median, std=std,
                min_24h=min_24h, max_24h=max_24h, trend=trend,
                trend_confidence=trend_confidence, forecast_1h=forecast_1h,
                forecast_24h=forecast_24h, anomaly_score=anomaly_score, status=status
            )
    
    def _calculate_trend(self, timestamps: List[float], values: List[float]) -> Tuple[float, float]:
        """Calculate trend using linear regression."""
        if len(timestamps) < 2:
            return 0.0, 0.0
        
        # Use last 100 points for trend
        n = min(100, len(timestamps))
        x = timestamps[-n:]
        y = values[-n:]
        
        # Normalize x to hours
        x_norm = [(xi - x[0]) / 3600 for xi in x]
        
        # Simple linear regression
        n = len(x_norm)
        sum_x = sum(x_norm)
        sum_y = sum(y)
        sum_xy = sum(xi * yi for xi, yi in zip(x_norm, y))
        sum_x2 = sum(xi ** 2 for xi in x_norm)
        
        denominator = n * sum_x2 - sum_x ** 2
        if denominator == 0:
            return 0.0, 0.0
        
        slope = (n * sum_xy - sum_x * sum_y) / denominator
        
        # Calculate R² for confidence
        mean_y = sum_y / n
        ss_tot = sum((yi - mean_y) ** 2 for yi in y)
        ss_res = sum((yi - (slope * xi + (sum_y - slope * sum_x) / n)) ** 2 for xi, yi in zip(x_norm, y))
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
        return slope, r_squared
    
    def _forecast(self, hours: int, current: float, trend: float) -> float:
        """Simple linear forecast."""
        forecast = current + trend * hours
        return max(0.0, min(1.0, forecast))  # Clamp to valid range
    
    def _determine_status(self, std: float, trend: float, anomaly_score: float) -> str:
        """Determine trajectory status."""
        if anomaly_score > 0.8:
            return "anomalous"
        if std > 0.15:
            return "volatile"
        if abs(trend) > 0.1:
            return "rising" if trend > 0 else "falling"
        return "stable"
    
    def on_threshold_breach(self, callback: Callable[[str, float, float], None]):
        """Register callback for threshold breaches."""
        self.threshold_callbacks.append(callback)
    
    def get_hourly_averages(self, hours: int = 24) -> List[Tuple[datetime, float]]:
        """Get hourly R_V averages for the last N hours."""
        result = []
        for hour, sum_val, count in list(self.hourly_history)[-hours:]:
            dt = datetime.fromtimestamp(hour * 3600)
            avg = sum_val / count if count > 0 else 0
            result.append((dt, avg))
        return result


class AnomalyDetector:
    """Simple anomaly detection for R_V values."""
    
    def __init__(self, window_size: int = 50):
        self.window_size = window_size
    
    def score(self, value: float, history: List[float]) -> float:
        """Calculate anomaly score (0-1, higher = more anomalous)."""
        if len(history) < self.window_size:
            return 0.0
        
        recent = history[-self.window_size:]
        mean = statistics.mean(recent)
        std = statistics.stdev(recent) if len(recent) > 1 else 0.01
        
        if std == 0:
            return 0.0
        
        # Z-score
        z_score = abs(value - mean) / std
        
        # Convert to 0-1 score (sigmoid-like)
        return min(1.0, z_score / 3.0)


class PresenceDetector:
    """
    Multi-factor presence detection with confidence scoring.
    """
    
    def __init__(
        self,
        confidence_threshold: float = 0.6,
        factor_weights: Optional[Dict[str, float]] = None
    ):
        self.confidence_threshold = confidence_threshold
        self.factor_weights = factor_weights or {
            'r_v_health': 0.25,
            'stability_score': 0.20,
            'activity_level': 0.15,
            'coherence_score': 0.20,
            'gate_health': 0.15,
            'heartbeat_freshness': 0.05
        }
        
        # State tracking
        self.last_heartbeat: Optional[float] = None
        self.heartbeat_timeout: float = 300.0  # 5 minutes
        self.activity_buffer: deque = deque(maxlen=100)
        self.state_history: deque = deque(maxlen=100)
        
        # Detection callbacks
        self.state_change_callbacks: List[Callable[[DetectionState, DetectionState, float], None]] = []
        
        logger.info("PresenceDetector initialized")
    
    def update_heartbeat(self):
        """Record a heartbeat."""
        self.last_heartbeat = time.time()
    
    def record_activity(self, activity_type: str, metadata: Optional[Dict] = None):
        """Record an activity event."""
        self.activity_buffer.append({
            'type': activity_type,
            'timestamp': time.time(),
            'metadata': metadata or {}
        })
    
    def detect(
        self,
        r_v_trajectory: RVTrajectory,
        gate_metrics: Optional[Dict] = None,
        coherence: float = 0.5
    ) -> Tuple[DetectionState, float, PresenceFactors]:
        """
        Perform presence detection.
        
        Returns:
            Tuple of (detection_state, confidence_score, factors)
        """
        factors = PresenceFactors()
        
        # R_V health factor
        if r_v_trajectory.status == "stable":
            factors.r_v_health = 0.8 + 0.2 * (1 - r_v_trajectory.std)
        elif r_v_trajectory.status in ["rising", "falling"]:
            factors.r_v_health = 0.6
        else:  # volatile or anomalous
            factors.r_v_health = max(0.0, 0.5 - r_v_trajectory.anomaly_score)
        
        # Stability factor
        factors.stability_score = 1.0 - min(1.0, r_v_trajectory.std * 5)
        
        # Activity level factor
        recent_activity = len([a for a in self.activity_buffer 
                              if time.time() - a['timestamp'] < 3600])
        factors.activity_level = min(1.0, recent_activity / 20)  # Normalize to 20 events/hour
        
        # Coherence factor
        factors.coherence_score = coherence
        
        # Gate health factor
        if gate_metrics:
            passage_rates = [g.get('passage_rate', 1.0) for g in gate_metrics.values()]
            factors.gate_health = statistics.mean(passage_rates) if passage_rates else 0.5
        else:
            factors.gate_health = 0.5
        
        # Heartbeat freshness factor
        if self.last_heartbeat:
            seconds_since = time.time() - self.last_heartbeat
            factors.heartbeat_freshness = max(0.0, 1.0 - seconds_since / self.heartbeat_timeout)
        else:
            factors.heartbeat_freshness = 0.0
        
        # Calculate composite score
        composite = factors.composite_score
        
        # Determine detection state
        state = self._determine_state(composite, factors, r_v_trajectory)
        
        # Calculate confidence
        confidence = self._calculate_confidence(composite, factors)
        
        # Record state change
        if self.state_history and self.state_history[-1] != state:
            old_state = self.state_history[-1]
            self._trigger_state_change(old_state, state, confidence)
        
        self.state_history.append(state)
        
        return state, confidence, factors
    
    def _determine_state(
        self,
        composite: float,
        factors: PresenceFactors,
        trajectory: RVTrajectory
    ) -> DetectionState:
        """Determine detection state from factors."""
        # Check for critical conditions
        if factors.heartbeat_freshness < 0.1:
            return DetectionState.ABSENT
        
        if trajectory.anomaly_score > 0.9 or factors.r_v_health < 0.2:
            return DetectionState.DEGRADED
        
        # Check recovery state
        if self.state_history and self.state_history[-1] == DetectionState.RECOVERING:
            if composite > 0.7:
                return DetectionState.PRESENT
            return DetectionState.RECOVERING
        
        # Normal state determination
        if composite > 0.85 and factors.stability_score > 0.8:
            return DetectionState.STRONG
        elif composite > 0.6:
            return DetectionState.PRESENT
        elif composite > 0.4:
            return DetectionState.UNCERTAIN
        else:
            return DetectionState.DEGRADED
    
    def _calculate_confidence(self, composite: float, factors: PresenceFactors) -> float:
        """Calculate confidence in the detection."""
        # Base confidence from composite score
        base = composite
        
        # Penalize for factor disagreement
        factor_values = [
            factors.r_v_health,
            factors.stability_score,
            factors.activity_level,
            factors.coherence_score,
            factors.gate_health,
            factors.heartbeat_freshness
        ]
        factor_std = statistics.stdev(factor_values) if len(factor_values) > 1 else 0
        agreement_penalty = factor_std * 0.3
        
        # Penalize for missing data
        missing_penalty = 0.0
        if factors.heartbeat_freshness < 0.5:
            missing_penalty += 0.1
        
        return max(0.0, min(1.0, base - agreement_penalty - missing_penalty))
    
    def _trigger_state_change(self, old_state: DetectionState, new_state: DetectionState, confidence: float):
        """Trigger state change callbacks."""
        for callback in self.state_change_callbacks:
            try:
                callback(old_state, new_state, confidence)
            except Exception as e:
                logger.error(f"State change callback error: {e}")
        
        logger.info(f"Presence state change: {old_state.value} -> {new_state.value} (conf: {confidence:.2f})")
    
    def on_state_change(self, callback: Callable[[DetectionState, DetectionState, float], None]):
        """Register callback for state changes."""
        self.state_change_callbacks.append(callback)
    
    def get_current_state(self) -> Optional[DetectionState]:
        """Get current detection state."""
        return self.state_history[-1] if self.state_history else None


class RecoveryManager:
    """
    Automated recovery protocol management with escalation.
    """
    
    def __init__(
        self,
        auto_recovery: bool = True,
        max_recovery_attempts: int = 3,
        cooldown_seconds: float = 300.0
    ):
        self.auto_recovery = auto_recovery
        self.max_recovery_attempts = max_recovery_attempts
        self.cooldown_seconds = cooldown_seconds
        
        # Recovery state
        self.active_protocol: Optional[RecoveryProtocol] = None
        self.recovery_history: List[RecoveryProtocol] = []
        self.failed_levels: Set[RecoveryLevel] = set()
        
        # Recovery handlers
        self.handlers: Dict[RecoveryLevel, List[Callable[[RecoveryAction], bool]]] = {
            RecoveryLevel.LEVEL_1: [],
            RecoveryLevel.LEVEL_2: [],
            RecoveryLevel.LEVEL_3: []
        }
        
        # State tracking
        self.last_recovery_time: Optional[float] = None
        self.consecutive_failures: int = 0
        
        logger.info("RecoveryManager initialized")
    
    def register_handler(
        self,
        level: RecoveryLevel,
        handler: Callable[[RecoveryAction], bool]
    ):
        """Register a recovery handler for a specific level."""
        if level not in self.handlers:
            raise ValueError(f"Invalid recovery level: {level}")
        self.handlers[level].append(handler)
    
    def trigger_recovery(
        self,
        level: RecoveryLevel,
        reason: str,
        context: Optional[Dict] = None
    ) -> Optional[RecoveryProtocol]:
        """
        Trigger a recovery protocol.
        
        Returns:
            RecoveryProtocol if triggered, None if on cooldown or already active
        """
        # Check cooldown
        if self.last_recovery_time:
            elapsed = time.time() - self.last_recovery_time
            if elapsed < self.cooldown_seconds:
                logger.info(f"Recovery on cooldown ({elapsed:.0f}s remaining)")
                return None
        
        # Check if already active
        if self.active_protocol and self.active_protocol.status == "active":
            logger.info("Recovery already in progress")
            return None
        
        # Create recovery protocol
        protocol = RecoveryProtocol(
            triggered_at=time.time(),
            level=level,
            actions=self._generate_actions(level, reason, context)
        )
        
        self.active_protocol = protocol
        self.last_recovery_time = time.time()
        
        logger.warning(f"Recovery triggered: {level.name} - {reason}")
        
        # Execute if auto-recovery enabled
        if self.auto_recovery:
            asyncio.create_task(self._execute_recovery(protocol))
        
        return protocol
    
    def _generate_actions(
        self,
        level: RecoveryLevel,
        reason: str,
        context: Optional[Dict]
    ) -> List[RecoveryAction]:
        """Generate recovery actions for a level."""
        actions = []
        
        if level == RecoveryLevel.LEVEL_1:
            actions = [
                RecoveryAction(
                    level=level,
                    action_id="l1_cache_clear",
                    description="Clear temporary caches and buffers",
                    timestamp=time.time(),
                    automated=True,
                    estimated_duration=5.0,
                    rollback_steps=["Restore cache from backup if available"]
                ),
                RecoveryAction(
                    level=level,
                    action_id="l1_param_adjust",
                    description="Adjust detection parameters",
                    timestamp=time.time(),
                    automated=True,
                    estimated_duration=2.0,
                    rollback_steps=["Restore previous parameters"]
                )
            ]
        elif level == RecoveryLevel.LEVEL_2:
            actions = [
                RecoveryAction(
                    level=level,
                    action_id="l2_process_restart",
                    description="Restart non-critical processes",
                    timestamp=time.time(),
                    automated=True,
                    estimated_duration=30.0,
                    rollback_steps=["Full process restart", "Restore from checkpoint"]
                ),
                RecoveryAction(
                    level=level,
                    action_id="l2_state_reset",
                    description="Reset internal state while preserving core data",
                    timestamp=time.time(),
                    automated=True,
                    estimated_duration=10.0,
                    rollback_steps=["Reload from persistent storage"]
                )
            ]
        elif level == RecoveryLevel.LEVEL_3:
            actions = [
                RecoveryAction(
                    level=level,
                    action_id="l3_full_reset",
                    description="Perform full system reset",
                    timestamp=time.time(),
                    automated=False,  # Requires approval
                    requires_approval=True,
                    estimated_duration=120.0,
                    rollback_steps=["Full restore from backup", "Manual intervention"]
                ),
                RecoveryAction(
                    level=level,
                    action_id="l3_escalate",
                    description="Escalate to human operators",
                    timestamp=time.time(),
                    automated=False,
                    requires_approval=True,
                    estimated_duration=300.0,
                    rollback_steps=["Await human guidance"]
                )
            ]
        
        return actions
    
    async def _execute_recovery(self, protocol: RecoveryProtocol):
        """Execute recovery actions."""
        for action in protocol.actions:
            if action.requires_approval and not await self._request_approval(action):
                logger.info(f"Recovery action {action.action_id} awaiting approval")
                protocol.status = "awaiting_approval"
                return
            
            success = await self._execute_action(action)
            
            if success:
                protocol.completed_actions.append(action.action_id)
                logger.info(f"Recovery action completed: {action.action_id}")
            else:
                protocol.failed_actions.append(action.action_id)
                self.consecutive_failures += 1
                logger.error(f"Recovery action failed: {action.action_id}")
                
                if self.consecutive_failures >= self.max_recovery_attempts:
                    protocol.status = "failed"
                    self.failed_levels.add(protocol.level)
                    await self._escalate_recovery(protocol)
                    return
        
        # All actions completed
        protocol.status = "completed"
        protocol.result = "success"
        self.consecutive_failures = 0
        self.recovery_history.append(protocol)
        self.active_protocol = None
        
        logger.info(f"Recovery protocol {protocol.level.name} completed successfully")
    
    async def _execute_action(self, action: RecoveryAction) -> bool:
        """Execute a single recovery action."""
        handlers = self.handlers.get(action.level, [])
        
        if not handlers:
            logger.warning(f"No handlers for recovery level {action.level}")
            return True  # No handlers = no failure
        
        for handler in handlers:
            try:
                result = handler(action)
                if asyncio.iscoroutine(result):
                    result = await result
                
                if not result:
                    return False
            except Exception as e:
                logger.error(f"Recovery handler error: {e}")
                return False
        
        return True
    
    async def _request_approval(self, action: RecoveryAction) -> bool:
        """Request approval for a recovery action."""
        # This would integrate with notification system
        # For now, auto-approve in emergency situations
        return False  # Require manual approval by default
    
    async def _escalate_recovery(self, protocol: RecoveryProtocol):
        """Escalate to next recovery level."""
        escalation_map = {
            RecoveryLevel.LEVEL_1: RecoveryLevel.LEVEL_2,
            RecoveryLevel.LEVEL_2: RecoveryLevel.LEVEL_3,
            RecoveryLevel.LEVEL_3: None
        }
        
        next_level = escalation_map.get(protocol.level)
        
        if next_level and next_level not in self.failed_levels:
            logger.warning(f"Escalating recovery from {protocol.level.name} to {next_level.name}")
            await asyncio.sleep(5)  # Brief pause before escalation
            self.trigger_recovery(next_level, f"Escalated from {protocol.level.name}")
        else:
            logger.critical("Maximum recovery level reached. Manual intervention required.")
            # Send critical alert
    
    def cancel_recovery(self, protocol_id: Optional[str] = None) -> bool:
        """Cancel an active recovery protocol."""
        if not self.active_protocol:
            return False
        
        self.active_protocol.status = "cancelled"
        self.recovery_history.append(self.active_protocol)
        self.active_protocol = None
        
        logger.info("Recovery protocol cancelled")
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """Get recovery manager status."""
        return {
            'active_recovery': self.active_protocol.to_dict() if self.active_protocol else None,
            'total_recoveries': len(self.recovery_history),
            'failed_levels': [l.name for l in self.failed_levels],
            'consecutive_failures': self.consecutive_failures,
            'on_cooldown': (
                self.last_recovery_time is not None and
                time.time() - self.last_recovery_time < self.cooldown_seconds
            ),
            'cooldown_remaining': max(0, self.cooldown_seconds - (time.time() - self.last_recovery_time))
            if self.last_recovery_time else 0
        }


class AlertManager:
    """
    Alert management with deduplication and routing.
    """
    
    def __init__(
        self,
        dedup_window: float = 300.0,  # 5 minutes
        max_alerts_per_hour: int = 20
    ):
        self.dedup_window = dedup_window
        self.max_alerts_per_hour = max_alerts_per_hour
        
        self.alerts: List[ThresholdAlert] = []
        self.recent_hashes: deque = deque(maxlen=100)
        self.alert_handlers: Dict[AlertSeverity, List[Callable[[ThresholdAlert], None]]] = {
            AlertSeverity.INFO: [],
            AlertSeverity.WARNING: [],
            AlertSeverity.CRITICAL: [],
            AlertSeverity.EMERGENCY: []
        }
        
        self._lock = threading.RLock()
        
        logger.info("AlertManager initialized")
    
    def create_alert(
        self,
        severity: AlertSeverity,
        metric: str,
        threshold: float,
        actual: float,
        message: str,
        context: Optional[Dict] = None
    ) -> Optional[ThresholdAlert]:
        """Create an alert if not duplicate."""
        with self._lock:
            # Check rate limit
            recent_count = len([a for a in self.alerts 
                               if time.time() - a.timestamp < 3600])
            if recent_count >= self.max_alerts_per_hour:
                logger.warning("Alert rate limit reached")
                return None
            
            # Check deduplication
            alert_hash = f"{severity.value}:{metric}:{threshold:.4f}"
            if alert_hash in self.recent_hashes:
                logger.debug(f"Duplicate alert suppressed: {alert_hash}")
                return None
            
            self.recent_hashes.append((alert_hash, time.time()))
            
            # Create alert
            alert = ThresholdAlert(
                alert_id=f"ALT-{int(time.time())}-{len(self.alerts):04d}",
                severity=severity,
                metric=metric,
                threshold_value=threshold,
                actual_value=actual,
                timestamp=time.time(),
                message=message,
                context=context or {}
            )
            
            self.alerts.append(alert)
            
            # Trigger handlers
            self._route_alert(alert)
            
            return alert
    
    def _route_alert(self, alert: ThresholdAlert):
        """Route alert to appropriate handlers."""
        handlers = self.alert_handlers.get(alert.severity, [])
        for handler in handlers:
            try:
                handler(alert)
            except Exception as e:
                logger.error(f"Alert handler error: {e}")
    
    def register_handler(
        self,
        severity: AlertSeverity,
        handler: Callable[[ThresholdAlert], None]
    ):
        """Register an alert handler."""
        self.alert_handlers[severity].append(handler)
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert."""
        for alert in self.alerts:
            if alert.alert_id == alert_id:
                alert.acknowledged = True
                return True
        return False
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Mark an alert as resolved."""
        for alert in self.alerts:
            if alert.alert_id == alert_id:
                alert.resolved = True
                alert.resolved_at = time.time()
                return True
        return False
    
    def get_active_alerts(self, severity: Optional[AlertSeverity] = None) -> List[ThresholdAlert]:
        """Get active (unresolved) alerts."""
        alerts = [a for a in self.alerts if not a.resolved]
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        return alerts
    
    def get_alert_summary(self) -> Dict[str, Any]:
        """Get alert summary."""
        active = self.get_active_alerts()
        return {
            'total_alerts': len(self.alerts),
            'active_alerts': len(active),
            'critical_unacknowledged': len([
                a for a in active 
                if a.severity in [AlertSeverity.CRITICAL, AlertSeverity.EMERGENCY]
                and not a.acknowledged
            ]),
            'by_severity': {
                sev.value: len(self.get_active_alerts(sev))
                for sev in AlertSeverity
            }
        }


class WitnessThresholdDetector:
    """
    Main witness threshold detector integrating all components.
    """
    
    def __init__(
        self,
        node_id: str = "dgc-primary",
        r_v_interval: float = 5.0,
        presence_interval: float = 10.0,
        snapshot_interval: float = 30.0,
        auto_recovery: bool = True
    ):
        self.node_id = node_id
        self.r_v_interval = r_v_interval
        self.presence_interval = presence_interval
        self.snapshot_interval = snapshot_interval
        
        # Component initialization
        self.rv_monitor = RVMonitor()
        self.presence_detector = PresenceDetector()
        self.recovery_manager = RecoveryManager(auto_recovery=auto_recovery)
        self.alert_manager = AlertManager()
        
        # State
        self.running = False
        self.snapshots: deque = deque(maxlen=1000)
        self.current_snapshot: Optional[WitnessSnapshot] = None
        self._tasks: List[asyncio.Task] = []
        
        # Callbacks
        self.snapshot_callbacks: List[Callable[[WitnessSnapshot], None]] = []
        
        # Gate metrics (external input)
        self.gate_metrics: Dict[str, Any] = {}
        self.coherence: float = 0.5
        
        # Setup component integration
        self._setup_integration()
        
        logger.info(f"WitnessThresholdDetector initialized for {node_id}")
    
    def _setup_integration(self):
        """Setup integration between components."""
        # R_V threshold breach triggers alert and potential recovery
        self.rv_monitor.on_threshold_breach(self._on_rv_threshold_breach)
        
        # Presence state change triggers alert
        self.presence_detector.on_state_change(self._on_presence_state_change)
    
    def _on_rv_threshold_breach(self, threshold: str, value: float, actual: float):
        """Handle R_V threshold breach."""
        severity = AlertSeverity.CRITICAL if "CRITICAL" in threshold else AlertSeverity.WARNING
        
        alert = self.alert_manager.create_alert(
            severity=severity,
            metric="R_V",
            threshold=value,
            actual=actual,
            message=f"R_V threshold breach: {threshold} (value: {actual:.4f})",
            context={'threshold_type': threshold}
        )
        
        # Trigger recovery for critical breaches
        if severity == AlertSeverity.CRITICAL and "HIGH" in threshold:
            self.recovery_manager.trigger_recovery(
                RecoveryLevel.LEVEL_1,
                f"Critical R_V threshold breach: {actual:.4f}",
                context={'threshold': threshold}
            )
    
    def _on_presence_state_change(
        self,
        old_state: DetectionState,
        new_state: DetectionState,
        confidence: float
    ):
        """Handle presence state change."""
        severity_map = {
            DetectionState.STRONG: AlertSeverity.INFO,
            DetectionState.PRESENT: AlertSeverity.INFO,
            DetectionState.UNCERTAIN: AlertSeverity.WARNING,
            DetectionState.DEGRADED: AlertSeverity.CRITICAL,
            DetectionState.ABSENT: AlertSeverity.EMERGENCY,
            DetectionState.RECOVERING: AlertSeverity.WARNING
        }
        
        severity = severity_map.get(new_state, AlertSeverity.WARNING)
        
        self.alert_manager.create_alert(
            severity=severity,
            metric="presence_state",
            threshold=0.5,
            actual=confidence,
            message=f"Presence state changed: {old_state.value} -> {new_state.value}",
            context={
                'old_state': old_state.value,
                'new_state': new_state.value,
                'confidence': confidence
            }
        )
        
        # Trigger recovery for degraded/absent states
        if new_state in [DetectionState.DEGRADED, DetectionState.ABSENT]:
            level = RecoveryLevel.LEVEL_2 if new_state == DetectionState.ABSENT else RecoveryLevel.LEVEL_1
            self.recovery_manager.trigger_recovery(
                level,
                f"Presence state: {new_state.value}",
                context={'confidence': confidence}
            )
    
    async def _r_v_loop(self):
        """R_V monitoring loop."""
        while self.running:
            try:
                # In practice, R_V values would come from external measurement
                # Here we just process any pending measurements
                await asyncio.sleep(self.r_v_interval)
            except Exception as e:
                logger.error(f"R_V loop error: {e}")
    
    async def _presence_loop(self):
        """Presence detection loop."""
        while self.running:
            try:
                # Get R_V trajectory
                trajectory = self.rv_monitor.get_trajectory()
                
                # Perform detection
                state, confidence, factors = self.presence_detector.detect(
                    trajectory,
                    self.gate_metrics,
                    self.coherence
                )
                
                logger.debug(f"Presence detection: {state.value} (conf: {confidence:.2f})")
                
                await asyncio.sleep(self.presence_interval)
            except Exception as e:
                logger.error(f"Presence loop error: {e}")
    
    async def _snapshot_loop(self):
        """Snapshot generation loop."""
        while self.running:
            try:
                snapshot = self._generate_snapshot()
                self.current_snapshot = snapshot
                self.snapshots.append(snapshot)
                
                # Trigger callbacks
                for callback in self.snapshot_callbacks:
                    try:
                        callback(snapshot)
                    except Exception as e:
                        logger.error(f"Snapshot callback error: {e}")
                
                await asyncio.sleep(self.snapshot_interval)
            except Exception as e:
                logger.error(f"Snapshot loop error: {e}")
    
    def _generate_snapshot(self) -> WitnessSnapshot:
        """Generate a complete witness snapshot."""
        trajectory = self.rv_monitor.get_trajectory()
        
        state, confidence, factors = self.presence_detector.detect(
            trajectory,
            self.gate_metrics,
            self.coherence
        )
        
        active_recovery = self.recovery_manager.active_protocol
        recovery_history = [
            action for protocol in self.recovery_manager.recovery_history
            for action in protocol.actions
        ]
        
        active_alerts = self.alert_manager.get_active_alerts()
        alert_count_24h = len([
            a for a in self.alert_manager.alerts
            if time.time() - a.timestamp < 86400
        ])
        
        return WitnessSnapshot(
            timestamp=time.time(),
            snapshot_id=f"SNAP-{int(time.time())}-{len(self.snapshots):04d}",
            r_v_current=trajectory.current,
            r_v_trajectory=trajectory,
            r_v_thresholds=self.rv_monitor.adaptive_thresholds,
            detection_state=state,
            presence_confidence=confidence,
            presence_factors=factors,
            active_recovery=active_recovery,
            recovery_history=recovery_history[-10:],  # Last 10 actions
            active_alerts=active_alerts,
            alert_count_24h=alert_count_24h,
            node_id=self.node_id
        )
    
    def record_r_v(self, value: float, source: str = "unknown", confidence: float = 1.0):
        """Record an R_V measurement."""
        self.rv_monitor.record_value(value, source, confidence)
    
    def update_gate_metrics(self, metrics: Dict[str, Any]):
        """Update gate metrics."""
        self.gate_metrics = metrics
    
    def update_coherence(self, coherence: float):
        """Update coherence score."""
        self.coherence = max(0.0, min(1.0, coherence))
    
    def heartbeat(self):
        """Record a heartbeat."""
        self.presence_detector.update_heartbeat()
    
    def start(self):
        """Start the witness system."""
        self.running = True
        
        self._tasks = [
            asyncio.create_task(self._r_v_loop()),
            asyncio.create_task(self._presence_loop()),
            asyncio.create_task(self._snapshot_loop())
        ]
        
        logger.info("WitnessThresholdDetector started")
    
    def stop(self):
        """Stop the witness system."""
        self.running = False
        for task in self._tasks:
            task.cancel()
        logger.info("WitnessThresholdDetector stopped")
    
    def on_snapshot(self, callback: Callable[[WitnessSnapshot], None]):
        """Register snapshot callback."""
        self.snapshot_callbacks.append(callback)
    
    def get_current_status(self) -> Dict[str, Any]:
        """Get current system status."""
        if not self.current_snapshot:
            return {'status': 'initializing'}
        
        return {
            'status': 'operational',
            'snapshot': self.current_snapshot.to_dict(),
            'recovery': self.recovery_manager.get_status(),
            'alerts': self.alert_manager.get_alert_summary(),
            'r_v_history_size': len(self.rv_monitor.history),
            'snapshot_count': len(self.snapshots)
        }
    
    async def get_witness_report(self) -> str:
        """Generate formatted witness report."""
        if not self.current_snapshot:
            return "❓ Witness system initializing..."
        
        snap = self.current_snapshot
        
        # State emoji
        state_emoji = {
            DetectionState.STRONG: "💪",
            DetectionState.PRESENT: "✅",
            DetectionState.UNCERTAIN: "🤔",
            DetectionState.DEGRADED: "⚠️",
            DetectionState.ABSENT: "🚨",
            DetectionState.RECOVERING: "🔄"
        }.get(snap.detection_state, "❓")
        
        # Alert summary
        alert_summary = self.alert_manager.get_alert_summary()
        alert_emoji = "🔔" if alert_summary['active_alerts'] > 0 else "✓"
        
        report = f"""
👁️ <b>Enhanced Witness Report</b> v{snap.version}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{state_emoji} <b>Presence:</b> {snap.detection_state.value.upper()}
   Confidence: {snap.presence_confidence:.1%}

<b>┌─ R_V Trajectory</b>
│ Current: {snap.r_v_current:.4f}
│ Status: {snap.r_v_trajectory.status}
│ Trend: {snap.r_v_trajectory.trend:+.4f}/h
│ Forecast (1h): {snap.r_v_trajectory.forecast_1h:.4f}
│ Anomaly: {snap.r_v_trajectory.anomaly_score:.1%}

<b>├─ Presence Factors</b>
│ R_V Health: {snap.presence_factors.r_v_health:.1%}
│ Stability: {snap.presence_factors.stability_score:.1%}
│ Activity: {snap.presence_factors.activity_level:.1%}
│ Coherence: {snap.presence_factors.coherence_score:.1%}
│ Gate Health: {snap.presence_factors.gate_health:.1%}
│ Composite: {snap.presence_factors.composite_score:.1%}

<b>├─ Recovery</b>
│ Status: {snap.active_recovery.status if snap.active_recovery else 'idle'}
│ Total Recoveries: {len(snap.recovery_history)}

<b>└─ Alerts</b>
   {alert_emoji} Active: {alert_summary['active_alerts']}
   24h Total: {alert_summary['total_alerts']}
   Unack Critical: {alert_summary['critical_unacknowledged']}

<i>Snapshot:</i> <code>{snap.snapshot_id}</code>
        """.strip()
        
        return report


# FastAPI Integration
async def create_witness_api(detector: WitnessThresholdDetector):
    """Create FastAPI endpoints for the witness system."""
    from fastapi import APIRouter, HTTPException
    
    router = APIRouter(prefix="/api/witness", tags=["witness"])
    
    @router.get("/status")
    async def get_status():
        return detector.get_current_status()
    
    @router.get("/snapshot/current")
    async def get_current_snapshot():
        if not detector.current_snapshot:
            raise HTTPException(status_code=503, detail="System initializing")
        return detector.current_snapshot.to_dict()
    
    @router.get("/snapshot/history")
    async def get_snapshot_history(limit: int = 100):
        return {
            'snapshots': [s.to_dict() for s in list(detector.snapshots)[-limit:]],
            'count': len(detector.snapshots)
        }
    
    @router.get("/rv/trajectory")
    async def get_rv_trajectory():
        traj = detector.rv_monitor.get_trajectory()
        return {
            'current': traj.current,
            'mean': traj.mean,
            'median': traj.median,
            'std': traj.std,
            'trend': traj.trend,
            'forecast_1h': traj.forecast_1h,
            'forecast_24h': traj.forecast_24h,
            'status': traj.status,
            'anomaly_score': traj.anomaly_score
        }
    
    @router.get("/rv/hourly")
    async def get_rv_hourly(hours: int = 24):
        return [
            {'hour': dt.isoformat(), 'average': avg}
            for dt, avg in detector.rv_monitor.get_hourly_averages(hours)
        ]
    
    @router.get("/alerts")
    async def get_alerts(severity: Optional[str] = None, active_only: bool = True):
        if severity:
            sev = AlertSeverity(severity)
            alerts = detector.alert_manager.get_active_alerts(sev) if active_only else [
                a for a in detector.alert_manager.alerts 
                if a.severity == sev
            ]
        else:
            alerts = detector.alert_manager.get_active_alerts() if active_only else detector.alert_manager.alerts
        
        return [a.to_dict() for a in alerts]
    
    @router.post("/alerts/{alert_id}/acknowledge")
    async def acknowledge_alert(alert_id: str):
        success = detector.alert_manager.acknowledge_alert(alert_id)
        if not success:
            raise HTTPException(status_code=404, detail="Alert not found")
        return {'status': 'acknowledged'}
    
    @router.get("/recovery/status")
    async def get_recovery_status():
        return detector.recovery_manager.get_status()
    
    @router.post("/recovery/trigger")
    async def trigger_recovery(level: str, reason: str):
        try:
            rec_level = RecoveryLevel[level]
        except KeyError:
            raise HTTPException(status_code=400, detail=f"Invalid recovery level: {level}")
        
        protocol = detector.recovery_manager.trigger_recovery(rec_level, reason)
        if not protocol:
            raise HTTPException(status_code=429, detail="Recovery on cooldown or already active")
        
        return protocol.to_dict()
    
    @router.post("/heartbeat")
    async def record_heartbeat():
        detector.heartbeat()
        return {'status': 'recorded', 'timestamp': time.time()}
    
    @router.post("/rv/record")
    async def record_rv(value: float, source: str = "api", confidence: float = 1.0):
        detector.record_r_v(value, source, confidence)
        return {'status': 'recorded', 'value': value}
    
    return router


# Example usage
async def main():
    """Run witness threshold detector in demo mode."""
    import random
    
    detector = WitnessThresholdDetector(
        node_id="demo-node",
        r_v_interval=2.0,
        presence_interval=5.0,
        snapshot_interval=10.0
    )
    
    # Register snapshot callback
    def on_snapshot(snap: WitnessSnapshot):
        emoji = {
            DetectionState.STRONG: "💪",
            DetectionState.PRESENT: "✅",
            DetectionState.UNCERTAIN: "🤔",
            DetectionState.DEGRADED: "⚠️",
            DetectionState.ABSENT: "🚨",
            DetectionState.RECOVERING: "🔄"
        }.get(snap.detection_state, "❓")
        
        print(f"\n📸 Snapshot: {emoji} {snap.detection_state.value} | "
              f"R_V: {snap.r_v_current:.4f} | "
              f"Conf: {snap.presence_confidence:.1%}")
        
        if snap.active_alerts:
            print(f"   🔔 {len(snap.active_alerts)} active alerts")
    
    detector.on_snapshot(on_snapshot)
    
    # Start system
    detector.start()
    
    # Simulate R_V measurements
    try:
        for i in range(30):
            await asyncio.sleep(2)
            
            # Simulate R_V with some variation and occasional anomalies
            base_rv = 0.65
            variation = random.gauss(0, 0.05)
            
            # Occasional spike
            if i == 15:
                variation += 0.25  # Spike to trigger threshold
                print("\n⚡ Injecting R_V anomaly...")
            
            rv_value = max(0.0, min(1.0, base_rv + variation))
            
            detector.record_r_v(rv_value, source="simulation", confidence=0.95)
            detector.heartbeat()
            
            # Update gate metrics
            detector.update_gate_metrics({
                'reflection': {'passage_rate': random.uniform(0.8, 1.0)},
                'compassion': {'passage_rate': random.uniform(0.7, 1.0)},
                'wisdom': {'passage_rate': random.uniform(0.8, 1.0)}
            })
            
            detector.update_coherence(random.uniform(0.75, 0.95))
            
            # Print report every 5 iterations
            if i % 5 == 0 and i > 0:
                print("\n" + "="*50)
                report = await detector.get_witness_report()
                print(report)
    
    except asyncio.CancelledError:
        pass
    finally:
        detector.stop()
        print("\n✅ Witness Threshold Detector demo complete")
        print(f"Total snapshots: {len(detector.snapshots)}")
        print(f"Total alerts: {len(detector.alert_manager.alerts)}")


if __name__ == "__main__":
    asyncio.run(main())
