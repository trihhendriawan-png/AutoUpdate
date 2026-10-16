"""
Lightweight Local HTTP Server for Xoilac M3U8 Playlist.
Serves xoilac.m3u over local network (LAN) with proper CORS and MIME headers,
plus a responsive status web dashboard.
"""

import os
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
import socket

logger = logging.getLogger(__name__)


def create_handler(playlist_path: str):
    class PlaylistHTTPHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            # 1. Endpoint: /xoilac.m3u
            if self.path.startswith("/xoilac.m3u") or self.path.startswith("/playlist.m3u"):
                if os.path.exists(playlist_path):
                    try:
                        with open(playlist_path, "rb") as f:
                            content = f.read()

                        self.send_response(200)
                        self.send_header("Content-Type", "application/vnd.apple.mpegurl; charset=utf-8")
                        self.send_header("Content-Disposition", 'inline; filename="xoilac.m3u"')
                        self.send_header("Access-Control-Allow-Origin", "*")
                        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
                        self.send_header("Content-Length", str(len(content)))
                        self.end_headers()
                        self.wfile.write(content)
                        return
                    except Exception as e:
                        self.send_error(500, f"Error reading playlist: {e}")
                        return
                else:
                    self.send_error(404, "Playlist xoilac.m3u belum dibuat.")
                    return

            # 2. Status Web Dashboard: /
            elif self.path == "/" or self.path == "/index.html":
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()

                # Get host IP
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    s.connect(("8.8.8.8", 80))
                    host_ip = s.getsockname()[0]
                    s.close()
                except Exception:
                    host_ip = "localhost"

                port = self.server.server_port
                m3u_url = f"http://{host_ip}:{port}/xoilac.m3u"

                # Read summary if available
                file_status = "Tersedia" if os.path.exists(playlist_path) else "Belum Dibuat"
                file_size = f"{os.path.getsize(playlist_path) / 1024:.1f} KB" if os.path.exists(playlist_path) else "0 KB"

                html = f"""<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Xoilac M3U8 Playlist Server</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background: #0f172a;
            color: #f8fafc;
            margin: 0;
            padding: 2rem;
            display: flex;
            justify-content: center;
        }}
        .card {{
            background: #1e293b;
            border-radius: 1rem;
            padding: 2rem;
            max-width: 650px;
            width: 100%;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
            border: 1px solid #334155;
        }}
        h1 {{
            color: #38bdf8;
            margin-top: 0;
            font-size: 1.75rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        .badge {{
            display: inline-block;
            background: #22c55e;
            color: #0f172a;
            font-size: 0.75rem;
            font-weight: 700;
            padding: 0.25rem 0.6rem;
            border-radius: 9999px;
            text-transform: uppercase;
        }}
        .url-box {{
            background: #090d16;
            border: 1px solid #475569;
            border-radius: 0.5rem;
            padding: 1rem;
            margin: 1.5rem 0;
            font-family: monospace;
            font-size: 1.05rem;
            color: #4ade80;
            word-break: break-all;
            user-select: all;
        }}
        .btn {{
            background: #0284c7;
            color: white;
            text-decoration: none;
            padding: 0.75rem 1.25rem;
            border-radius: 0.5rem;
            font-weight: 600;
            display: inline-block;
            transition: background 0.2s;
        }}
        .btn:hover {{
            background: #0369a1;
        }}
        .stats {{
            margin-top: 1.5rem;
            padding-top: 1.5rem;
            border-top: 1px solid #334155;
            font-size: 0.9rem;
            color: #94a3b8;
        }}
    </style>
</head>
<body>
    <div class="card">
        <h1>Xoilac M3U8 Server <span class="badge">Online</span></h1>
        <p>Server playlist otomatis berjalan aktif di jaringan lokal Anda.</p>
        
        <h3>URL Playlist Anda:</h3>
        <div class="url-box">{m3u_url}</div>
        
        <p>Salin URL di atas ke aplikasi IPTV Anda (TiviMate, IPTV Smarters, VLC, Televizo, OTT Navigator).</p>
        
        <a class="btn" href="/xoilac.m3u" download="xoilac.m3u">Download xoilac.m3u</a>
        
        <div class="stats">
            <p><strong>Status File:</strong> {file_status} ({file_size})</p>
            <p><strong>Lokasi Host:</strong> {host_ip}:{port}</p>
        </div>
    </div>
</body>
</html>"""
                self.wfile.write(html.encode("utf-8"))
                return

            else:
                self.send_error(404, "Endpoint not found.")

        def log_message(self, format, *args):
            # Suppress excessive HTTP access logs in console
            pass

    return PlaylistHTTPHandler


def run_local_server(port: int, playlist_path: str):
    """Starts the HTTP server."""
    handler = create_handler(playlist_path)
    server = HTTPServer(("0.0.0.0", port), handler)
    logger.info(f"Server HTTP aktif di port {port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
