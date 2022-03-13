import logging
import constants

#variable that defines if the logging has started to set the logging configuration in the first attempt
logging_started = False


def start_logging():
    """
    this function is used to start the logging that will be used in the exception handler

    Returns
    -------
    None.

    """
    global logging_started
    if(logging_started == False):
        #if the logging is being started set the the directory of the logfile to the one defined in the constants folder
        logging.basicConfig(filename=constants.LOGFILE_DIR, encoding='utf-8', level=logging.DEBUG, format='%(asctime)s %(message)s')
        logging_started = True
        
        
def exception_handler(func):
    """
    this function acts as a decorator that handles the exceptions thrown during the execution of the decorated functions
    
    this function takes the decorated functions, starts the logging, inputs log messages and logs exceptions in cases where they are returned

    Parameters
    ----------
    func : TYPE
        the decorated function that will have its' exceptions handled by this function.

    Returns
    -------
    TYPE
        this function returns itself as it acts as it is used as a decorator for another inner function.

    """
    def inner_function(*args, **kwargs):
        try:
            #call this function to start the logging and setup the logging configuration
            start_logging()
            logging.debug("Launching the function " + func.__name__)
            return func(*args, **kwargs)
        except Exception as exception:
            #if an exception is returned log the exception
            logging.error("function returned an Exception with message: " + str(exception))
    return inner_function