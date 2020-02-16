import logging
import logging.handlers

class LogRecorder(object):
    def __init__(self):
        self._log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        #self._log_file = log_file
        self._log_name = __name__
        self._log_level = logging.DEBUG
        logging.basicConfig

        self.handler = logging.StreamHandler()
        self.handler.setFormatter(logging.Formatter(self._log_format))
        self.handler.setLevel = logging.ERROR

        
        self._logger = logging.getLogger(self._log_name)
        self._logger.setLevel(self._log_level)
        self._logger.propagate=False
        #self._logger.removeHandler(StreamHandler)
        
        

    def debug_log(self, content):
        self._logger.addHandler(self.handler)
        self._logger.debug(content)

    def info_log(self, content):
        self._logger.addHandler(self.handler)
        self._logger.info(content)

    def warning_log(self, content):
        self._logger.addHandler(self.handler)
        self._logger.warning(content)

    def error_log(self, content):
        self._logger.addHandler(self.handler)
        self._logger.error(content)

    def critical_log(self, content):
        self._logger.addHandler(self.handler)
        self._logger.critical(content)
        
    def exception_log(self, content):
        self._logger.addHandler(self.handler)
        self._logger.exception(content)

if __name__=='__main__':

    logger = LogRecorder()
    #logger.debug_log("debug log")    
    logger.info_log("log system is ok")
    #logger.warning_log("warning log")
    #logger.error_log("error log")
    #logger.critical_log('critical log')