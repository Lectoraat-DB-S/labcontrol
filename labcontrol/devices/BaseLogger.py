import logging
import logging.config

#logging.config.fileConfig('logging.conf')

# create logger
logger = logging.getLogger(__name__)

logging.basicConfig(
    filename="labcontrol.log",
    encoding="utf-8",
    filemode="a",
    format="{asctime} - {levelname} - {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M",
    )
