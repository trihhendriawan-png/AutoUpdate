"""
Main CLI Application for Automated Xoilac M3U8 Playlist System.
Handles scraping, whitelist filtering, stream resolution, file generation,
background auto-refresh daemon, and built-in local HTTP streaming server.
"""

import sys
import time
import argparse
import logging
import socket
from typing import List, Dict

from config import (
    OUTPUT_FILE,
    UPDATE_INTERVAL_SECONDS,
    LOCAL_SERVER_PORT,
    INCLUDE_UPCOMING_MATCHES
)
from scraper import MatchScraper
from generator import PlaylistGenerator
from server import run_local_server

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("XoilacM3U")


def get_local_ip() -> str:
    """Detects local LAN IP address for Smart TV connection."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def run_pipeline() -> List[Dict]:
    """
    Executes a single pass of the playlist generation pipeline.
    """
    logger.info("=" * 60)
    logger.info("Memulai proses update Playlist Xoilac M3U8...")
    logger.info("=" * 60)

    scraper = MatchScraper()
    generator = PlaylistGenerator(OUTPUT_FILE)

    # 1. Fetch whitelisted matches
    logger.info("1. Mengambil jadwal dan memfilter pertandingan sesuai whitelist...")
    matches = scraper.fetch_all_matches()

    if not matches:
        logger.warning("Tidak ditemukan pertandingan yang cocok dengan whitelist saat ini.")
        # If no matches, generate minimal template
        content = generator.build_m3u([])
        generator.save_to_file(content)
        return []

    live_count = sum(1 for m in matches if m.get("is_live"))
    upcoming_count = len(matches) - live_count

    logger.info(f"Ditemukan {len(matches)} pertandingan whitelist (LIVE: {live_count}, UPCOMING: {upcoming_count}).")

    # 2. Resolve stream URLs for matches
    logger.info("2. Menghubungkan pertandingan dengan URL stream...")
    for idx, match in enumerate(matches, 1):
        home = match["home_team"]
        away = match["away_team"]
        comp = match["competition"]
        is_live = match["is_live"]
        status_tag = "LIVE" if is_live else "UPCOMING"

        logger.info(f"  [{idx}/{len(matches)}] ({status_tag}) [{comp}] {home} vs {away}...")
        streams = scraper.resolve_streams_for_match(match)
        match["streams"] = streams
        if streams:
            logger.info(f"      -> {len(streams)} stream ditemukan: {streams[0]}")
        else:
            logger.info("      -> Menyiapkan link siaran standby.")

    # 3. Filter out upcoming if disabled
    final_matches = matches
    if not INCLUDE_UPCOMING_MATCHES:
        final_matches = [m for m in matches if m.get("is_live")]

    # 4. Generate M3U
    logger.info("3. Menghasilkan file xoilac.m3u...")
    content = generator.build_m3u(final_matches)
    generator.save_to_file(content)

    # 5. Display Summary Statistics
    logger.info("-" * 60)
    logger.info("RINGKASAN PLAYLIST BERHASIL DIPERBARUI:")
    logger.info(f"- Lokasi File   : {OUTPUT_FILE}")
    logger.info(f"- Total Entri   : {len(final_matches)} Pertandingan")
    logger.info(f"- Pertandingan LIVE : {sum(1 for m in final_matches if m.get('is_live'))}")
    logger.info(f"- Pertandingan Nanti: {sum(1 for m in final_matches if not m.get('is_live'))}")

    # Category breakdown
    cat_counts = {}
    for m in final_matches:
        c = m.get("category", "Lainnya")
        cat_counts[c] = cat_counts.get(c, 0) + 1

    for cat, cnt in cat_counts.items():
        logger.info(f"  * {cat}: {cnt} pertandingan")
    logger.info("-" * 60)

    return final_matches


def main():
    parser = argparse.ArgumentParser(description="Xoilac Automatic M3U8 Playlist Generator")
    parser.add_argument(
        "--watch",
        action="store_true",
        help="Jalankan secara otomatis terus-menerus (daemon loop) memperbarui playlist"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=UPDATE_INTERVAL_SECONDS,
        help=f"Interval pembaruan dalam detik jika mode --watch aktif (default: {UPDATE_INTERVAL_SECONDS} detik)"
    )
    parser.add_argument(
        "--serve",
        action="store_true",
        help="Nyalakan web server lokal agar URL m3u bisa langsung diakses Smart TV / VLC di Wi-Fi lokal"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=LOCAL_SERVER_PORT,
        help=f"Port untuk server HTTP lokal (default: {LOCAL_SERVER_PORT})"
    )

    args = parser.parse_args()

    # Initial generation pass
    run_pipeline()

    local_ip = get_local_ip()
    playlist_url = f"http://{local_ip}:{args.port}/xoilac.m3u"

    if args.serve:
        logger.info("=" * 60)
        logger.info("SERVER HTTP LOKAL AKTIF:")
        logger.info(f"URL Playlist Smart TV / VLC: {playlist_url}")
        logger.info("Salin URL di atas dan masukkan ke IPTV Smarters / TiviMate / VLC!")
        logger.info("=" * 60)

        # Start server in background thread if watch is also requested, or run server directly
        import threading
        server_thread = threading.Thread(
            target=run_local_server,
            args=(args.port, OUTPUT_FILE),
            daemon=True
        )
        server_thread.start()

    if args.watch:
        logger.info(f"Mode Auto-Refresh Aktif. Memperbarui playlist setiap {args.interval} detik...")
        try:
            while True:
                time.sleep(args.interval)
                run_pipeline()
        except KeyboardInterrupt:
            logger.info("Program dihentikan oleh pengguna.")
            sys.exit(0)
    elif args.serve:
        logger.info("Server sedang berjalan. Tekan Ctrl+C untuk keluar.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Server dihentikan.")
            sys.exit(0)


if __name__ == "__main__":
    main()
