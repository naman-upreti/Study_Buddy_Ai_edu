# This file contains the settings for the application
#selecting the model for the application
#MODEL_NAME = "llama-3.1-8b-instant"

import os
from dotenv import load_dotenv

load_dotenv()

class Settings():

    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

    MODEL_NAME = "llama-3.1-8b-instant"
    
    TEMPERATURE = 0.9
    # this define the creativity of the model

    # this define the number of times the model will retry when it gets an error
    MAX_RETRIES = 3
    # this define the maximum number of tokens the model can generate

settings = Settings()  

# this is the instance of the class that will be used throughout the application
