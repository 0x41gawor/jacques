from dotenv import load_dotenv
load_dotenv()

import os
import time
import argparse
import logging

from common.db.executor import PostgresExecutor
from common.logging.config import configure_logging

from app.config import load_config
from app.repo.ingestion_sources import IngestionSourceRepository
from app.service.identity_api_service import IdentityApiService
from app.service.ingestion_runner import IngestionRunner
from app.service.prov_api_client import ProvApiService
from app.service.readwise_service import ReadwiseService


def parse_args():
    parser = argparse.ArgumentParser(description="Jacques Ingestion Worker")

    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set logging level",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    level = getattr(logging, args.log_level.upper())
    configure_logging(level=level)

    cfg = load_config()

    db = PostgresExecutor()

    source_repo = IngestionSourceRepository(db=db)
    readwise_service = ReadwiseService(readwise_url=cfg.readwise_url)
    identity_api_service = IdentityApiService(
        base_url=os.environ["IDENTITY_API_BASE_URL"],
        internal_service_token=os.environ["INTERNAL_SERVICE_TOKEN"],
    )
    prov_api_service = ProvApiService(prov_api_url=cfg.prov_api_url)

    runner = IngestionRunner(
        source_repo=source_repo,
        readwise_service=readwise_service,
        identity_api_client=identity_api_service,
        prov_api_client=prov_api_service,
    )

    while True:
        runner.run_once(batch_size=cfg.batch_size)
        time.sleep(cfg.poll_interval_seconds)


if __name__ == "__main__":
    main()