import logging
logger = logging.getLogger(__name__)

def download_regatta(args):
    url = args["url"]
    logger.info(f"download_regatta({url})")
