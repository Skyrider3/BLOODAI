import os
from openai import OpenAI
import uuid

# Assuming you have a secret key for JWT signing
os.environ["SECRET_KEY"] = str(uuid.uuid4())
os.environ["ALGORITHM"] = "HS256"
# os.environ["Database"] = "sqlite:///./test.db"
#GPT - Key
# os.environ["client"] = OpenAI(api_key="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") # modify this so that the app.py variable will fetch the api key from here