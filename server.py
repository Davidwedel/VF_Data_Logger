#!/usr/bin/env python3
import argparse
import http.server
import os
import re
import socketserver
import sys
import threading
import time
from pathlib import Path
from typing import List
import json

# Try to import watchdog; fall back to polling if not available.
USE_WATCHDOG = True
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except Exception:
    USE_WATCHDOG = False

XML_START = "<!-- XML_LIST_START -->"
XML_END = "<!-- XML_LIST_END -->"

def find_xmls(watch_dir: Path) -> List[Path]:
    return sorted(p for p in watch_dir.glob("*.xml") if p.is_file())

def render_list(xml_files: List[Path], web_root: Path) -> str:
    # Make hrefs relative to the served root
    items = []
    for p in xml_files:
        rel = p.relative_to(web_root)
        items.append(f'<li><a href="{rel.as_posix()}">{rel.name}</a></li>')
    return "<ul>\n" + "\n".join(items) + "\n</ul>"

def rewrite_index(index_path: Path, watch_dir: Path, web_root: Path) -> None:
    if not index_path.exists():
        print(f"[WARN] index.html not found at {index_path}")
        return

    with index_path.open("r", encoding="utf-8") as f:
        html = f.read()

    start_idx = html.find(XML_START)
    end_idx = html.find(XML_END)

    if start_idx == -1 or end_idx == -1 or end_idx < start_idx:
        print(f"[ERROR] Couldn't find XML markers in {index_path}. "
              f"Add `{XML_START}` and `{XML_END}` to your index.html.")
        return

    xml_files = find_xmls(watch_dir)
    new_block = XML_START + "\n" + render_list(xml_files, web_root) + "\n" + XML_END

    new_html = html[:start_idx] + new_block + html[end_idx + len(XML_END):]

    tmp_path = index_path.with_suffix(".html.tmp")
    with tmp_path.open("w", encoding="utf-8") as f:
        f.write(new_html)
    tmp_path.replace(index_path)

    print(f"[INFO] index.html updated: {len(xml_files)} XML file(s) listed.")

def serve_http(web_root: Path, port: int):
    os.chdir(web_root)
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("0.0.0.0", port), handler) as httpd:
        print(f"[INFO] Serving {web_root} at http://0.0.0.0:{port}")
        httpd.serve_forever()

def watch_with_watchdog(watch_dir: Path, index_path: Path, web_root: Path):
    class Handler(FileSystemEventHandler):
        def on_any_event(self, event):
            # We only care about *.xml creates/deletes/moves/modifies
            if event.is_directory:
                return
            if event.src_path.endswith(".xml") or getattr(event, "dest_path", "").endswith(".xml"):
                rewrite_index(index_path, watch_dir, web_root)

    observer = Observer()
    observer.schedule(Handler(), str(watch_dir), recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

def watch_with_polling(watch_dir: Path, index_path: Path, web_root: Path, interval: float = 2.0):
    last = None
    try:
        while True:
            current = tuple(p.name for p in find_xmls(watch_dir))
            if current != last:
                rewrite_index(index_path, watch_dir, web_root)
                last = current
            time.sleep(interval)
    except KeyboardInterrupt:
        pass

def main():
    # Load secrets
    with open("secrets.json", "r") as f:
        secrets = json.load(f)

    parser = argparse.ArgumentParser(description="Watch a dir for XML files and update index.html, serving over HTTP.")
    parser.add_argument("--port", type=int, default=8000, help="HTTP port to serve on.")
    parser.add_argument("--poll", action="store_true", help="Force polling instead of watchdog.")
    args = parser.parse_args()

    web_root = Path("./webserver").resolve()
    watch_dir = Path(secrets["path_to_xmls"]).resolve()
    index_path = web_root / "index.html"


    # Check watch_dir
    if not watch_dir.exists():
        raise FileNotFoundError(f"watch_dir does not exist: {watch_dir}")
        sys.exit(1)

    if not web_root.exists():
        print(f"[ERROR] web-root does not exist: {web_root}")
        sys.exit(1)

    # First build
    rewrite_index(index_path, watch_dir, web_root)

    # Start HTTP server on a thread
    t = threading.Thread(target=serve_http, args=(web_root, args.port), daemon=True)
    t.start()

    # Watch
    if not args.poll and USE_WATCHDOG:
        print("[INFO] Using watchdog for file watching.")
        watch_with_watchdog(watch_dir, index_path, web_root)
    else:
        if not USE_WATCHDOG and not args.poll:
            print("[WARN] watchdog not available, falling back to polling. `pip install watchdog` for better performance.")
        print("[INFO] Polling for changes...")
        watch_with_polling(watch_dir, index_path, web_root)

if __name__ == "__main__":
    main()

