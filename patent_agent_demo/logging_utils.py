import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Optional

LOG_DIR = "/workspace/output/logs"
SYSTEM_LOG = "system.log"


def ensure_logs_dir(path: Optional[str] = None) -> str:
    base = path or LOG_DIR
    try:
        os.makedirs(base, exist_ok=True)
    except Exception:
        pass
    return base


def setup_root_file_logging(base_dir: Optional[str] = None, level: int = logging.INFO):
    log_dir = ensure_logs_dir(base_dir)
    # Extra guard to create directory
    try:
        os.makedirs(log_dir, exist_ok=True)
    except Exception:
        pass
    root = logging.getLogger()
    root.setLevel(level)
    # Avoid duplicate handlers
    existing = any(isinstance(h, RotatingFileHandler) and getattr(h, "_is_system", False) for h in root.handlers)
    if not existing:
        fh = RotatingFileHandler(os.path.join(log_dir, SYSTEM_LOG), maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8", delay=True)
        fh.setLevel(level)
        fh._is_system = True  # marker
        fmt = logging.Formatter(fmt="%(asctime)s %(levelname)s %(name)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
        fh.setFormatter(fmt)
        root.addHandler(fh)
    # Always keep console handler
    if not any(isinstance(h, logging.StreamHandler) for h in root.handlers):
        ch = logging.StreamHandler()
        ch.setLevel(level)
        ch.setFormatter(logging.Formatter(fmt="%(levelname)s %(name)s: %(message)s"))
        root.addHandler(ch)


def attach_agent_file_logger(agent_name: str, base_dir: Optional[str] = None) -> logging.Logger:
    log_dir = ensure_logs_dir(base_dir)
    # Extra guard to create directory
    try:
        os.makedirs(log_dir, exist_ok=True)
    except Exception:
        pass
    logger = logging.getLogger(f"agent.{agent_name}")
    logger.setLevel(logging.INFO)
    # Avoid duplicate handlers
    agent_log_path = os.path.join(log_dir, f"{agent_name}.log")
    if not any(isinstance(h, RotatingFileHandler) and getattr(h, "_agent_name", None) == agent_name for h in logger.handlers):
        fh = RotatingFileHandler(agent_log_path, maxBytes=3 * 1024 * 1024, backupCount=2, encoding="utf-8", delay=True)
        fh.setLevel(logging.INFO)
        fh._agent_name = agent_name
        fh.setFormatter(logging.Formatter(fmt="%(asctime)s %(levelname)s %(name)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
        logger.addHandler(fh)
    return logger