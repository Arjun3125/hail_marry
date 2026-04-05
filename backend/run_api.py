"""Unified API launcher with stdout-first server logging."""
from __future__ import annotations

import argparse
import os
import sys

import uvicorn


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the VidyaOS API server.")
    parser.add_argument("--host", default=os.getenv("HOST", "0.0.0.0"))
    parser.add_argument("--port", type=int, default=int(os.getenv("PORT", "8080")))
    parser.add_argument("--workers", type=int, default=int(os.getenv("WEB_CONCURRENCY", "1")))
    parser.add_argument("--reload", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    print(
        f"[backend-api] Starting uvicorn host={args.host} port={args.port} workers={args.workers} reload={args.reload}",
        flush=True,
    )
    try:
        uvicorn.run(
            "main:app",
            host=args.host,
            port=args.port,
            workers=args.workers,
            reload=args.reload,
            log_config=None,
            access_log=True,
        )
    except Exception as exc:
        print(f"[backend-api] Fatal startup error before port bind: {exc}", file=sys.stderr, flush=True)
        raise


if __name__ == "__main__":
    main()
