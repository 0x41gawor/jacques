# app/main.py
from dotenv import load_dotenv
load_dotenv()
import os
import flask

import argparse
import logging

from app.factory import create_app


from common.logging.config import configure_logging

def parse_args():
    parser = argparse.ArgumentParser(description="Jacques Prov API")

    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set logging level",
    )

    return parser.parse_args()

def main():
    args = parse_args()
    # Zamiana string → logging level
    level = getattr(logging, args.log_level.upper())

    configure_logging(level=level)

    app = create_app()
    port = os.environ.get("BANDARI")
    app.run(host="0.0.0.0", port=port, debug=True)

if __name__ == "__main__":  
    main()