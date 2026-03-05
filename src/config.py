"""
Config Loader & Logging Setup
==============================
Membaca config.yaml dan menyiapkan logging terpusat.
"""

import logging
import os
from pathlib import Path

import yaml


# Root directory proyek (satu level di atas src/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_ROOT / "config.yaml"


def load_config(config_path: Path = CONFIG_PATH) -> dict:
    """
    Membaca file konfigurasi YAML.

    Parameters
    ----------
    config_path : Path
        Path ke file config.yaml.

    Returns
    -------
    dict
        Dictionary berisi seluruh konfigurasi proyek.
    """
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return config


def setup_logging(config: dict) -> logging.Logger:
    """
    Menyiapkan logging terpusat berdasarkan konfigurasi.

    Parameters
    ----------
    config : dict
        Dictionary konfigurasi dari load_config().

    Returns
    -------
    logging.Logger
        Logger utama proyek.
    """
    log_cfg = config.get("logging", {})
    level = getattr(logging, log_cfg.get("level", "INFO").upper(), logging.INFO)
    fmt = log_cfg.get("format", "%(asctime)s | %(levelname)-8s | %(message)s")

    logging.basicConfig(level=level, format=fmt, force=True)
    logger = logging.getLogger("quant_project")
    logger.setLevel(level)

    return logger


def ensure_output_dir(config: dict) -> Path:
    """
    Membuat direktori output jika belum ada.

    Returns
    -------
    Path
        Path ke direktori output.
    """
    output_dir = PROJECT_ROOT / config["output"]["directory"]
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir
