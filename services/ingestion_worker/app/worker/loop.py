from common import logger

from app.worker.backoff import exponential_backoff

def run_loop(task_runner, poll_interval: int, shutdown_event):
    
    logger.info("Starting ingestion worker loop.")
    attempt = 0

    while not shutdown_event.is_set():
        try:
            task_runner.run()
            attempt = 0
        except Exception as e:
            logger.error(f"Error running task: {e}")
            attempt += 1
            exponential_backoff(attempt)

        logger.info(f"Waiting for {poll_interval} seconds before next run.")
        shutdown_event.wait(poll_interval)

    logger.info("Ingestion worker loop has been stopped.")