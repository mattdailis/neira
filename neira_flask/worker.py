import os
import sys
import signal
import traceback
import psycopg
from psycopg.rows import dict_row
import logging

from neira_flask import jobs

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Flag to control graceful shutdown
running = True

def signal_handler(sig, frame):
    global running
    logger.info(f"Received signal {sig}, shutting down gracefully...")
    running = False

# Register signal handlers for graceful shutdown
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

job_handlers = {
    "download_regatta": jobs.download_regatta
}

def process_job(job):
    """
    Process a single job from the jobs table.

    Args:
        job: Dict containing job data with keys like id, job_type, arguments, etc.
    """
    logger.info(f"Processing job {job['id']}: {job.get('job_type', 'unknown')}")

    handler = job_handlers.get(job['job_type'])
    if handler is None:
        logger.error(f"Unknown job type: {job['job_type']}")
        return

    handler(job['arguments'])
    logger.info(f"Job {job['id']} processed successfully")
    

def fetch_and_process_job(job_id):
    """
    Fetch a job by ID and process it, updating its status.

    Args:
        conn: Database connection
        job_id: ID of the job to process
    """
    with psycopg.connect(os.environ.get('DATABASE_URL')) as conn:
        with conn.cursor(row_factory=dict_row) as cursor:
            # Fetch the job with FOR UPDATE SKIP LOCKED to prevent concurrent processing
            cursor.execute("""
                UPDATE neira.jobs
                SET status = 'processing',
                    started_at = NOW()
                WHERE id = %s
                AND status = 'pending'
                returning id, job_type, arguments;
            """, (job_id,))

            job = cursor.fetchone()

            if not job:
                logger.debug(f"Job {job_id} already processed or not found")
                return
            
            try:
                process_job(job)

                # Mark job as completed
                cursor.execute("""
                    UPDATE neira.jobs
                    SET status = 'completed',
                        completed_at = NOW()
                    WHERE id = %s
                """, (job_id,))


                logger.info("committing")
                conn.commit()

            except Exception as e:
                logger.error(f"Error processing job {job_id}: {e}", exc_info=True)

                error_details = traceback.format_exc()

                # Mark job as failed
                cursor.execute("""
                    UPDATE neira.jobs
                    SET status = 'failed',
                        error_message = %s,
                        completed_at = NOW()
                    WHERE id = %s
                """, (error_details, job_id))

                conn.commit()

def listen_for_jobs():
    """
    Main worker loop that listens for job notifications and processes them.
    """
    database_url = os.environ.get('DATABASE_URL')

    if not database_url:
        logger.error("DATABASE_URL environment variable not set")
        sys.exit(1)

    logger.info("Worker starting up...")

    while running:
        try:
            # Create a dedicated connection for LISTEN
            with psycopg.connect(database_url, autocommit=True) as conn:
                with conn.cursor() as cursor:
                    # Start listening to the jobs channel
                    cursor.execute("LISTEN new_job")
                    logger.info("Listening for new jobs on 'new_job' channel...")

                    # Also process any pending jobs on startup
                    logger.info("Processing any pending jobs...")
                    cursor.execute("""
                        SELECT id FROM neira.jobs
                        WHERE status = 'pending'
                        ORDER BY created_at ASC
                    """)
                    pending_jobs = cursor.fetchall()

                    for (job_id,) in pending_jobs:
                        if not running:
                            break
                        fetch_and_process_job(job_id)

                    logged_waiting = False
                    while running:
                        if not logged_waiting:
                            logger.info("waiting...")
                        logged_waiting = True
                        for notify in conn.notifies(timeout=5):
                            if not running:
                                break

                            logged_waiting = False
                            logger.info(f"Received notification: {notify.payload}")

                            try:
                                job_id, job_type = notify.payload.split(',')
                                job_id = int(job_id)
                                if job_type in job_handlers:
                                    fetch_and_process_job(job_id)
                                else:
                                    logger.info(f"No handler defined for job_type: '{job_type}'")
                            except Exception as e:
                                logger.error(f"Error processing notification: {e}", exc_info=True)
                            if not logged_waiting:
                                logger.info("waiting...")
                            logged_waiting = True

        except psycopg.OperationalError as e:
            if running:
                logger.error(f"Database connection error: {e}")
                logger.info("Retrying in 5 seconds...")
                import time
                time.sleep(5)
            else:
                break
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            if running:
                import time
                time.sleep(5)
            else:
                break

    logger.info("Worker shutting down...")
