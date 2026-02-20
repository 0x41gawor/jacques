import os
from dotenv import load_dotenv
load_dotenv()

import argparse

from app.factory import create_app

from common.logging.config import configure_logging

def parse_args():
    parser = argparse.ArgumentParser(description="Jacques Identity API")

    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set logging level",
    )

    return parser.parse_args()

def main():
    args = parse_args()

    configure_logging(args.log_level.upper())

    app = create_app()
    port = os.environ.get("TOKARI")
    app.run(host="0.0.0.0", port=port, debug=True)


if __name__ == "__main__":
    main()