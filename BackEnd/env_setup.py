import os

# Assuming you have a secret key for JWT signing
os.environ["SECRET_KEY"] = "your-secret-key"
os.environ["ALGORITHM"] = "HS256"
#GPT - Key
os.environ["client"] = OpenAI(api_key="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")