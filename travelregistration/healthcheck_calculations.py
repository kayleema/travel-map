import os
import resource
import sys

from django.db import connection


def _bytes_to_mebibytes(value):
    if value is None:
        return None
    return round(value / 1024 / 1024, 2)


def _get_load_average():
    if not hasattr(os, "getloadavg"):
        return None
    one, five, fifteen = os.getloadavg()
    return {
        "1m": round(one, 2),
        "5m": round(five, 2),
        "15m": round(fifteen, 2),
    }


def _get_system_memory():
    try:
        page_size = os.sysconf("SC_PAGE_SIZE")
        total_pages = os.sysconf("SC_PHYS_PAGES")
        available_pages = os.sysconf("SC_AVPHYS_PAGES")
    except (AttributeError, OSError, ValueError):
        return None

    total_bytes = page_size * total_pages
    available_bytes = page_size * available_pages
    return {
        "total_mb": _bytes_to_mebibytes(total_bytes),
        "available_mb": _bytes_to_mebibytes(available_bytes),
        "used_percent": round((1 - available_bytes / total_bytes) * 100, 1) if total_bytes else None,
    }


def _get_process_memory():
    max_rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    max_rss_bytes = max_rss if sys.platform == "darwin" else max_rss * 1024
    return {
        "max_rss_mb": _bytes_to_mebibytes(max_rss_bytes),
    }


def _get_database_health():
    try:
        connection.ensure_connection()
    except Exception as exc:
        return {
            "ok": False,
            "vendor": connection.vendor,
            "error": exc.__class__.__name__,
        }
    return {
        "ok": True,
        "vendor": connection.vendor,
    }
