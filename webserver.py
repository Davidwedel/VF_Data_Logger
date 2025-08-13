#!/usr/bin/env python3
"""
Serve a directory and always expose the newest XML file as latest.xml.

Requires:
  - secrets.json with: { "path_to_xmls": "/absolute/or/relative/path" }
  - (optional) watchdog: pip install watchdog
"""

import argparse
import http.server
import os
import shutil
import socketserver
import sys
import threading
import time
from pathlib import Path
from typing import List, Optional
import json

# Try to import watchdog; fall back to polling if not available.
USE_WATCHDOG = True
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except Exception:
    USE_WATCHDOG = False


# ------------------------- helpers -------------------------

def find_xmls(watch_dir: Path) -> List[Path]:
    return sorted(p for p in watch_dir.glob("*.xml") if p.is_file())

def newest_xml(watch_dir: Path) -> Optional[Path]:
    xmls = find_xmls(watch_dir)
    if not xmls:
        return None
    return max(xmls, key=lambda p: p.stat().st_mtime)

def publish_latest(watch_dir: Path, web_root: Path):
    latest = newest_xml(watch_dir)
    dest = web_root / "latest.xml"

    if latest is None:
        # Remove stale latest.xml if present
        if dest.exists() or dest.is_symlink():
            dest.unlink()
        print("[INFO] No XML files found; latest.xml removed (if existed).")
        return

    try:
        if dest.exists() or dest.is_symlink():
            dest.unlink()
        # Prefer symlink to avoid copying big files
        os.symlink(latest, dest)
        print(f"[INFO] Symlinked newest XML: {latest} -> {dest}")
    except OSError:
        shutil.copy2(latest, dest)
        print(f"[INFO] Copied newest XML: {latest} -> {dest}")

def serve_http(web_root: Path, port: int):
    os.chdir(web_root)
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("0.0.0.0", port), handler) as httpd:
        print(f"[INFO] Serving {web_root} at http://0.0.0.0:{port}")
        httpd.serve_forever()

def watch_with_watchdog(watch_dir: Path, web_root: Path):
    class Handler(FileSystemEventHandler):
        def on_any_event(self, event):
            if event.is_directory:
                return
            src = getattr(event, "src_path", "") or ""
            dst = getattr(event, "dest_path", "") or ""
            if src.endswith(".xml") or dst.endswith(".xml"):
                publish_latest(watch_dir, web_root)

    observer = Observer()
    observer.schedule(Handler(), str(watch_dir), recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

def watch_with_polling(watch_dir: Path, web_root: Path, interval: float = 2.0):
    last: Optional[tuple] = None
    try:
        while True:
            current = tuple(p.name for p in find_xmls(watch_dir))
            if current != last:
                publish_latest(watch_dir, web_root)
                last = current
            time.sleep(interval)
    except KeyboardInterrupt:
        pass


# --------------------------- main ---------------------------

def main():
    # Load secrets
    with open("secrets.json", "r", encoding="utf-8") as f:
        secrets = json.load(f)

    parser = argparse.ArgumentParser(
        description="Serve a web dir and expose newest XML as latest.xml."
    )
    parser.add_argument("--port", type=int, default=8000, help="HTTP port to serve on.")
    parser.add_argument("--poll", action="store_true", help="Force polling instead of watchdog.")
    parser.add_argument("--web-root", default="./webserver", help="Directory to serve (will host latest.xml).")
    args = parser.parse_args()

    web_root = Path(args.web_root).resolve()
    watch_dir = Path(secrets["path_to_xmls"]).resolve()

    if not watch_dir.exists():
        print(f"[ERROR] watch_dir does not exist: {watch_dir}")
        sys.exit(1)
    if not web_root.exists():
        print(f"[ERROR] web_root does not exist: {web_root}")
        sys.exit(1)

    # First publish newest XML
    publish_latest(watch_dir, web_root)

    # Start HTTP server on a thread
    t = threading.Thread(target=serve_http, args=(web_root, args.port), daemon=True)
    t.start()

    # Watch for changes
    if not args.poll and USE_WATCHDOG:
        print("[INFO] Using watchdog for file watching.")
        watch_with_watchdog(watch_dir, web_root)
    else:
        if not USE_WATCHDOG and not args.poll:
            print("[WARN] watchdog not available, falling back to polling. `pip install watchdog` for better performance.")
        print("[INFO] Polling for changes...")
        watch_with_polling(watch_dir, web_root)


if __name__ == "__main__":
    main()

