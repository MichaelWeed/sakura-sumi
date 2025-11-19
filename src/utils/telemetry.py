"""Lightweight telemetry logging for compression runs."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


class TelemetryLogger:
    """
    Appends JSONL telemetry events to the output directory.
    
    Logging is enabled by default but can be disabled by:
      - Setting the environment variable `SAKURA_TELEMETRY` to "0", "false", or "off"
      - Passing `enabled=False` when instantiating the logger (for advanced usage)
    """
    
    ENV_FLAG = "SAKURA_TELEMETRY"
    
    def __init__(self, output_dir: Path | str, enabled: Optional[bool] = None):
        self.output_dir = Path(output_dir)
        env_value = os.getenv(self.ENV_FLAG)
        
        if enabled is not None:
            self.enabled = enabled
        elif env_value is not None:
            self.enabled = env_value.strip().lower() not in {"0", "false", "off"}
        else:
            self.enabled = True
        
        self.log_path = self.output_dir / "telemetry.log"
    
    def log_event(self, event: str, payload: Dict[str, Any]) -> None:
        """Write a single telemetry entry if logging is enabled."""
        if not self.enabled:
            return
        
        entry = {
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
            "event": event,
            "payload": payload,
        }
        
        try:
            self.log_path.parent.mkdir(parents=True, exist_ok=True)
            with self.log_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(entry, default=str))
                handle.write("\n")
        except Exception as exc:
            # Telemetry should never block the pipeline; fail open with a warning.
            print(f"[telemetry] Failed to write event '{event}': {exc}")

