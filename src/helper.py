import chainlit as cl
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_classic.memory import ConversationBufferWindowMemory
from paystackapi.paystack import Paystack 
import os
from paystackapi.transaction import Transaction
import requests
from pinecone.grpc import PineconeGRPC as Pinecone
from twilio.rest import Client




# Load environment variables
load_dotenv()  

# Initialize APIs
paystack = Paystack(secret_key=os.getenv('PAYSTACK_SECRET_KEY'))
twilio_client = Client(os.getenv('TWILIO_ACCOUNT_SID'), os.getenv('TWILIO_AUTH_TOKEN'))
groq_api_key = os.getenv("GROQ_API_KEY")  

# Read API key from environment variable
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
if PINECONE_API_KEY is None:
    raise ValueError("PINECONE_API_KEY environment variable is not set.")

# Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY) 