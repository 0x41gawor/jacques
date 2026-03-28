from dotenv import load_dotenv
load_dotenv()

import os
import time
import argparse
import logging
import threading

from common.logging.config import configure_logging
from common.db.executor import PostgresExecutor

from app.config import load_config
from app.factory import create_app
from app.runtime import WorkerRuntimeState
from app.repo.ingestion_sources import IngestionSourceRepository
from app.service.identity_api_service import IdentityApiService
from app.service.ingestion_runner import IngestionRunner
from app.service.prov_api_client import ProvApiService
from app.service.readwise_service import ReadwiseService
from app.worker.shutdown import register_signal_handlers, shutdown_event


def parse_args():
    parser = argparse.ArgumentParser(description="Jacques Ingestion Worker")

    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set logging level",
    )

    return parser.parse_args()


def run_health_server(*, runtime_state, health_port: int, max_idle_seconds: int):
    app = create_app(
        runtime_state=runtime_state,
        max_idle_seconds=max_idle_seconds,
    )
    app.run(host="0.0.0.0", port=health_port, debug=False, use_reloader=False)


def main() -> None:
    args = parse_args()
    level = getattr(logging, args.log_level.upper())
    configure_logging(level=level)

    register_signal_handlers()

    cfg = load_config()
    runtime_state = WorkerRuntimeState()

    health_thread = threading.Thread(
        target=run_health_server,
        kwargs={
            "runtime_state": runtime_state,
            "health_port": 5000,
            "max_idle_seconds": cfg.health_max_idle_seconds,
        },
        daemon=True,
    )
    health_thread.start()

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
        max_attempts_per_word=cfg.max_attempts_per_word,
    )

    while not shutdown_event.is_set():
        runtime_state.mark_loop_started()

        try:
            runner.run_once(batch_size=cfg.batch_size)
            runtime_state.mark_loop_success()
        except Exception as e:
            runtime_state.mark_loop_failure(str(e))
            logging.getLogger(__name__).exception("Worker loop iteration failed")

        shutdown_event.wait(cfg.poll_interval_seconds)


if __name__ == "__main__":
    main()