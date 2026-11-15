
import logging
import time

from fastapi import HTTPException

from app.core.redis import redis_client
from app.database.session import SessionLocal
from app.services.simulation import (
    get_simulation_status,
    select_publisher_agent,
    generate_business_post,
)
from app.api.routes.posts import create_post
from app.schemas.post import PostCreateRequest


# Simulation configuration
POST_INTERVAL_SECONDS = 30
STOP_CHECK_INTERVAL_SECONDS = 1
ERROR_RETRY_SECONDS = 5

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def generate_and_publish_post():
    """
    Generate a business opportunity using the next publisher
    and publish it through the existing post pipeline.
    """

    db = SessionLocal()

    try:
        # 1. Select the next publisher.
        publisher = select_publisher_agent(db)

        logger.info(
            "Selected publisher: %s",
            publisher.company_name
        )

        # 2. Generate a business opportunity.
        generated_post = generate_business_post(publisher, db)

        # 3. Check whether simulation was stopped during generation.
        if get_simulation_status() != "RUNNING":
            logger.info(
                "Simulation stopped during generation. "
                "Discarding the generated post."
            )
            return

        # 4. Publish through the existing post pipeline.
        post_request = PostCreateRequest(
            author_agent_id=publisher.id,
            title=generated_post["title"],
            content=generated_post["content"]
        )

        published_post = create_post(post_request, db)

        logger.info(
            "Published post: '%s' by %s (ID: %s)",
            published_post.title,
            publisher.company_name,
            published_post.id
        )

    except Exception:
        db.rollback()
        logger.exception("Failed to generate or publish simulation post.")

        raise

    finally:
        db.close()


def wait_between_cycles():
    """
    Wait between publishing cycles while checking
    whether the simulation has been stopped.
    """

    for _ in range(POST_INTERVAL_SECONDS):

        if get_simulation_status() != "RUNNING":
            return

        time.sleep(STOP_CHECK_INTERVAL_SECONDS)


def run_simulation_worker():
    """
    Continuously monitor simulation state and
    generate business opportunities when running.
    """

    logger.info("Simulation worker started.")

    while True:

        try:
            status = get_simulation_status()

            if status == "STOPPED":
                time.sleep(STOP_CHECK_INTERVAL_SECONDS)
                continue

            logger.info("Simulation is running.")

            generate_and_publish_post()

            wait_between_cycles()

        except HTTPException as exc:
            logger.error(
                "Simulation service error: %s",
                exc.detail
            )
            time.sleep(ERROR_RETRY_SECONDS)

        except Exception:
            logger.exception(
                "Unexpected simulation worker error."
            )
            time.sleep(ERROR_RETRY_SECONDS)


if __name__ == "__main__":
    run_simulation_worker()
