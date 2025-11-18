import logging

def configure_logging():
    logging.basicConfig(level=logging.INFO)
    logging.getLogger('uvicorn').setLevel(logging.INFO)
