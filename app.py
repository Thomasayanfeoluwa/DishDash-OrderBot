import chainlit as cl
from src.helper import *
from store_index import *
from src.prompt import RAG_PROMPT, ORDER_SUMMARY_PROMPT, TWILIO_NOTIFICATION_PROMPT 
from datetime import datetime
from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from src.order_manager import order_manager
from src.payment_handler import payment_handler
from langchain_huggingface import HuggingFaceEmbeddings
from pinecone.grpc import PineconeGRPC as Pinecone
from langchain_pinecone import PineconeVectorStore
import json
import os



# Initialize Pinecone
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
pc = Pinecone(api_key=PINECONE_API_KEY)

@cl.on_chat_start
async def start():
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    index_name = "dashdishorderbot"
    
    # Connect to existing Pinecone index
    docsearch = PineconeVectorStore.from_existing_index(
        index_name=index_name,
        embedding=embeddings
    )

    # Initialize LLM
    llm = ChatGroq(
        groq_api_key=os.getenv("GROQ_API_KEY"),
        model_name="llama-3.1-70b-versatile",
        temperature=0.4,
        streaming=True
    )
    
    # Create RAG chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=docsearch.as_retriever(search_kwargs={"k": 3}),
        chain_type_kwargs={"prompt": RAG_PROMPT},
        return_source_documents=True
    )
    
    # Initialize session
    cl.user_session.set("qa_chain", qa_chain)
    cl.user_session.set("order_cart", [])
    cl.user_session.set("customer_info", {})
    cl.user_session.set("order_stage", "welcome")
    
    await cl.Message(content="""🍽️ **Welcome to DishDash OrderBot!** 🍽️

I can help you:
• Discover delicious Nigerian dishes
• Place orders seamlessly  
• Process secure payments
• Get food delivered to you

What would you like to do today?""").send()


async def handle_menu_query(message: cl.Message):
    """Handle dish recommendations using RAG"""
    qa_chain = cl.user_session.get("qa_chain")
    msg = cl.Message(content="")
    await msg.send()
    
    # Use RAG to get dish recommendations
    res = await qa_chain.acall(
        message.content,
        callbacks=[cl.AsyncLangchainCallbackHandler()]
    )
    
    answer = res["result"]
    response = f"{answer}\n\nWould you like to order any of these dishes? Just tell me what you'd like!"
    await cl.Message(content=response).send()

async def handle_general_query(message: cl.Message):
    """Handle general questions using RAG"""
    qa_chain = cl.user_session.get("qa_chain")
    msg = cl.Message(content="")
    await msg.send()
    
    res = await qa_chain.acall(
        message.content,
        callbacks=[cl.AsyncLangchainCallbackHandler()]
    )
    
    await cl.Message(content=res["result"]).send()

@cl.on_message
async def handle_message(message: cl.Message):
    user_input = message.content.lower()
    current_stage = cl.user_session.get("order_stage", "welcome")
    
    if current_stage == "collecting_phone":
        await handle_phone_input(message)
    elif current_stage == "collecting_location":
        await handle_location_input(message)
    elif current_stage == "collecting_instructions":
        await handle_instructions_input(message)
    elif any(keyword in user_input for keyword in ['order', 'buy', 'cart']):
        await start_order_process()
    elif any(keyword in user_input for keyword in ['menu', 'dishes', 'what do you have']):
        await handle_menu_query(message)  
    else:
        await handle_general_query(message)  

async def start_order_process():
    """Start the order collection process"""
    cl.user_session.set("order_stage", "collecting_phone")
    await cl.Message(content="📞 **Let's start your order!**\n\nPlease provide your phone number:").send()

async def handle_phone_input(message: cl.Message):
    """Handle phone number input"""
    phone = message.content.strip()
    cl.user_session.set("customer_info", {"phone": phone})
    cl.user_session.set("order_stage", "collecting_location")
    
    await cl.Message(content="📍 **Great! Now please provide your delivery location:**").send()

async def handle_location_input(message: cl.Message):
    """Handle location input"""
    location = message.content.strip()
    customer_info = cl.user_session.get("customer_info", {})
    customer_info["location"] = location
    cl.user_session.set("customer_info", customer_info)
    cl.user_session.set("order_stage", "collecting_instructions")
    
    await cl.Message(content="📝 **Any special instructions for your order?** (e.g., extra spicy, no onions, etc.)\n\nIf none, just type 'none'").send()

async def handle_instructions_input(message: cl.Message):
    """Handle special instructions"""
    instructions = "None" if message.content.lower() == "none" else message.content.strip()
    customer_info = cl.user_session.get("customer_info", {})
    customer_info["instructions"] = instructions
    cl.user_session.set("customer_info", customer_info)
    cl.user_session.set("order_stage", "ready")
    
    await cl.Message(content="""✅ **Perfect! You're all set!**

Now you can:
• Ask me about dishes using the RAG system
• Tell me what you'd like to order
• Type 'checkout' when you're ready to pay

What would you like to do?""").send()

@cl.action_callback("pay_now")
async def on_pay_now(action: cl.Action):
    """Handle pay now action"""
    reference = action.value
    # In a real app, you'd open the payment URL
    await cl.Message(content=f"Please visit the payment URL to complete your transaction. Reference: {reference}").send()

@cl.action_callback("verify_payment")
async def on_verify_payment(action: cl.Action):
    """Handle payment verification"""
    reference = action.value
    success = await order_manager.verify_and_complete_order(reference, cl.user_session)
    
    if success:
        cl.user_session.set("order_stage", "welcome")
    else:
        await cl.Message(content="Payment verification failed. Please try again or contact support.").send()

# Run the application
if __name__ == "__main__":
    cl.run()