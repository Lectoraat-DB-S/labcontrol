import logging


class TekLog():
    #def __init__(self) -> None:
    #    self.logger = logging.getLogger(__name__)
    #    logging.basicConfig(filename='TekScope.log', level=logging.INFO)
    #    self.logger.info('TekLogger Started')
    
    def __init__(self, fileName='TekScope.log') -> None:
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(filename=fileName,
                            format='%(asctime)s %(levelname)-8s %(message)s',
                            level=logging.INFO,
                            datefmt='%Y-%m-%d %H:%M:%S')
        #logging.basicConfig(filename=fileName, level=logging.INFO)
        self.logger.info('TekLogger Started')
    
    def addToLog(self, msg):
        self.logger.log(logging.INFO, msg)
    """  
    def addToLog(self, msg, logLevel):
        match logLevel:
            case logging.INFO:
                self.logger.log(logging.INFO, msg)
            case logging.ERROR:
                self.logger.log(logging.ERROR, msg)
            case logging.WARNING:
                self.logger.log(logging.WARNING, msg)
            case logging.DEBUG:
                self.logger.log(logging.DEBUG, msg)
            case logging.FATAL:
                self.logger.log(logging.FATAL, msg)
            case logging.NOTSET:
                self.logger.log(logging.CRITICAL, msg)
            case logging.CRITICAL:
                self.logger.log(logging.CRITICAL, msg)
            case _:
                self.logger.log(logging.CRITICAL, "Unknown loglevel!!! Message = ")
                self.logger.log(logging.CRITICAL, msg)
                
    """