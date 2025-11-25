import os
import sys
import signal
import psycopg
from psycopg.rows import dict_row
import logging

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

def process_job(job):
    """
    Process a single job from the jobs table.

    Args:
        job: Dict containing job data with keys like id, job_type, payload, etc.
    """
    logger.info(f"Processing job {job['id']}: {job.get('job_type', 'unknown')}")

    # TODO: Implement your job processing logic here
    # Example:
    # if job['job_type'] == 'apply_corrections':
    #     apply_corrections(job['payload'])
    # elif job['job_type'] == 'regenerate_visualizations':
    #     regenerate_visualizations(job['payload'])

    logger.info(f"Job {job['id']} processed successfully")

def fetch_and_process_job(conn, job_id):
    """
    Fetch a job by ID and process it, updating its status.

    Args:
        conn: Database connection
        job_id: ID of the job to process
    """
    logger.info("start fetch_and_process_job")
    with psycopg.connect(os.environ.get('DATABASE_URL')) as conn:
        with conn.cursor(row_factory=dict_row) as cursor:
            # Fetch the job with FOR UPDATE SKIP LOCKED to prevent concurrent processing
            logger.info("fetch_and_process_job 1")
            cursor.execute("""
                UPDATE neira.jobs
                SET status = 'processing',
                    started_at = NOW()
                WHERE id = %s
                AND status = 'pending'
                returning id;
            """, (job_id,))
            logger.info("fetch_and_process_job 2")

            job = cursor.fetchone()

            logger.info("fetch_and_process_job 3")

            if not job:
                logger.debug(f"Job {job_id} already processed or not found")
                return
            
            logger.info("fetch_and_process_job 4")

            try:
                logger.info("fetch_and_process_job 5")
                process_job(job)
                logger.info("fetch_and_process_job 6")

                # Mark job as completed
                cursor.execute("""
                    UPDATE neira.jobs
                    SET status = 'completed',
                        completed_at = NOW()
                    WHERE id = %s
                """, (job_id,))

                logger.info("fetch_and_process_job 7")

                logger.info("committing")
                conn.commit()

            except Exception as e:
                logger.info("fetch_and_process_job 8")
                logger.error(f"Error processing job {job_id}: {e}", exc_info=True)

                # Mark job as failed
                cursor.execute("""
                    UPDATE neira.jobs
                    SET status = 'failed',
                        error_message = %s,
                        completed_at = NOW()
                    WHERE id = %s
                """, (str(e), job_id))

                conn.commit()
            logger.info("fetch_and_process_job 9")

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
                    logger.info("01")
                    cursor.execute("""
                        SELECT id FROM neira.jobs
                        WHERE status = 'pending'
                        ORDER BY created_at ASC
                    """)
                    logger.info("12")
                    pending_jobs = cursor.fetchall()
                    logger.info("34")

                    for (job_id,) in pending_jobs:
                        if not running:
                            break
                        fetch_and_process_job(conn, job_id)

                    # Enter the notification loop
                    logger.info("pre-gen")
                    gen = conn.notifies()
                    logger.info("post-gen")
                    while running:
                        # Wait for notifications (with 1 second timeout)
                        try:
                            logger.info("waiting...")
                            notify = next(gen)

                            if not running:
                                logger.info("not running!")
                                break

                            logger.info(f"Received notification: {notify.payload}")

                            # The payload should be the job ID
                            try:
                                logger.info("try")
                                job_id = int(notify.payload)
                                logger.info(f"job_id: {job_id}")
                                fetch_and_process_job(conn, job_id)
                                logger.info(f"after fetch_and_process_job")
                            except ValueError:
                                logger.error(f"Invalid job ID in notification: {notify.payload}")
                            except Exception as e:
                                logger.error(f"Error processing notification: {e}", exc_info=True)
                        except StopIteration:
                            # Timeout - no notification received, continue loop
                            pass

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

if __name__ == "__main__":
    listen_for_jobs()