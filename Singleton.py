"""
singleton.py — Singleton Pattern
===================================
USE CASE: The CampusFind AI Matching Service configuration must be
consistent across all requests — the confidence threshold, text weight,
and image weight must have exactly one authoritative source at runtime.
Allowing multiple instances of the configuration would risk different
parts of the system using different thresholds simultaneously.

The Singleton pattern ensures only one MatchingConfig instance exists.
Super admins update the single instance; all services read from it.

Also demonstrated: DatabaseConnectionPool Singleton — only one pool
of DB connections should exist to prevent connection exhaustion.

PATTERN: __new__ is overridden to return the existing instance if one
already exists. Thread-safe version uses a Lock.
"""
import threading


# ── Singleton 1: Matching Configuration ──────────────────────────

class MatchingConfig:
    """
    Singleton — holds the AI matching engine configuration.
    Only one instance exists; all services read from and write to this instance.
    Thread-safe using a class-level Lock.
    """

    _instance = None
    _lock: threading.Lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                # Double-checked locking — re-check after acquiring lock
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialise()
        return cls._instance

    def _initialise(self) -> None:
        """Set default configuration values (called only once)."""
        self._confidence_threshold: float = 0.70
        self._text_weight: float = 0.60
        self._image_weight: float = 0.40
        self._max_retries: int = 3
        self._job_timeout_seconds: int = 60
        self._min_text_prefilter: float = 0.40

    # ── Properties ────────────────────────────────────────────────

    @property
    def confidence_threshold(self) -> float:
        return self._confidence_threshold

    @confidence_threshold.setter
    def confidence_threshold(self, value: float) -> None:
        if not 0.0 <= value <= 1.0:
            raise ValueError("Confidence threshold must be between 0.0 and 1.0.")
        self._confidence_threshold = value

    @property
    def text_weight(self) -> float:
        return self._text_weight

    @property
    def image_weight(self) -> float:
        return self._image_weight

    @property
    def max_retries(self) -> int:
        return self._max_retries

    @property
    def job_timeout_seconds(self) -> int:
        return self._job_timeout_seconds

    @property
    def min_text_prefilter(self) -> float:
        return self._min_text_prefilter

    def update(
        self,
        confidence_threshold: float = None,
        text_weight: float = None,
        image_weight: float = None,
    ) -> None:
        """Super admin updates configuration. Weights must sum to 1.0."""
        if text_weight is not None and image_weight is not None:
            if abs((text_weight + image_weight) - 1.0) > 0.001:
                raise ValueError("text_weight + image_weight must equal 1.0.")
            self._text_weight = text_weight
            self._image_weight = image_weight
        if confidence_threshold is not None:
            self.confidence_threshold = confidence_threshold

    def __repr__(self) -> str:
        return (
            f"MatchingConfig(threshold={self._confidence_threshold:.0%}, "
            f"text={self._text_weight}, image={self._image_weight})"
        )


# ── Singleton 2: Database Connection Pool ─────────────────────────

class DatabaseConnectionPool:
    """
    Singleton — ensures only one connection pool is created.
    Prevents connection exhaustion from multiple pool instantiations.
    """

    _instance = None
    _lock: threading.Lock = threading.Lock()

    def __new__(cls, dsn: str = "postgresql://localhost/campusfind"):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialise(dsn)
        return cls._instance

    def _initialise(self, dsn: str) -> None:
        self._dsn = dsn
        self._pool_size = 10
        self._active_connections = 0
        print(f"[DB Pool] Initialised connection pool → {dsn} (pool size: {self._pool_size})")

    @property
    def dsn(self) -> str:
        return self._dsn

    @property
    def active_connections(self) -> int:
        return self._active_connections

    def get_connection(self) -> str:
        """Simulate acquiring a connection from the pool."""
        if self._active_connections >= self._pool_size:
            raise RuntimeError("Connection pool exhausted. All connections are in use.")
        self._active_connections += 1
        return f"Connection-{self._active_connections}"

    def release_connection(self) -> None:
        if self._active_connections > 0:
            self._active_connections -= 1

    def __repr__(self) -> str:
        return (
            f"DatabaseConnectionPool(dsn={self._dsn}, "
            f"active={self._active_connections}/{self._pool_size})"
        )