import logging

def log(type, module_name, message):
    """
    Log the message to the system in a standard format.
    
    Args:
    type (str): The type of log (e.g., INFO, WARNING, ERROR).
    module_name (str): The name of the module or component logging the message.
    message (str): The log message.
    """
    logging.basicConfig(filename='tgbot.log',format='%(asctime)s - %(levelname)s - %(module)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)
    logging.log(getattr(logging, type.upper()), f"{module_name}: {message}")