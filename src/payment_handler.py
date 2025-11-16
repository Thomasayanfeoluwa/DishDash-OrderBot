import requests
import json
import os
import chainlit as cl
from langchain_groq import ChatGroq
from src.prompt import ORDER_SUMMARY_PROMPT, TWILIO_NOTIFICATION_PROMPT 
from twilio.rest import Client

class PaymentHandler:
    def __init__(self):
        self.paystack_secret_key = os.getenv('PAYSTACK_SECRET_KEY')
        self.paystack_public_key = os.getenv('PAYSTACK_PUBLIC_KEY')
        self.base_url = "https://api.paystack.co"
        self.twilio_client = Client(os.getenv('TWILIO_ACCOUNT_SID'), os.getenv('TWILIO_AUTH_TOKEN'))
    
    async def initialize_payment(self, email, amount, order_data, metadata=None):
        """Initialize Paystack payment"""
        try:
            # Convert amount to kobo 
            amount_kobo = int(amount * 100)
            
            # Prepare payment data
            payment_data = {
                "email": email,
                "amount": amount_kobo,
                "currency": "NGN",
                "metadata": metadata or {},
                "callback_url": "https://your-domain.com/verify-payment"  
            }
            
            # Add order data to metadata
            payment_data["metadata"]["order_data"] = json.dumps(order_data)
            
            # Make API request to Paystack
            headers = {
                "Authorization": f"Bearer {self.paystack_secret_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                f"{self.base_url}/transaction/initialize",
                headers=headers,
                json=payment_data
            )
            
            if response.status_code == 200:
                result = response.json()
                if result["status"]:
                    return {
                        "success": True,
                        "authorization_url": result["data"]["authorization_url"],
                        "access_code": result["data"]["access_code"],
                        "reference": result["data"]["reference"]
                    }
                else:
                    return {"success": False, "message": result["message"]}
            else:
                return {"success": False, "message": "Payment initialization failed"}
                
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    async def verify_payment(self, reference):
        """Verify Paystack payment"""
        try:
            headers = {
                "Authorization": f"Bearer {self.paystack_secret_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                f"{self.base_url}/transaction/verify/{reference}",
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                if result["status"] and result["data"]["status"] == "success":
                    return {
                        "success": True,
                        "data": result["data"],
                        "message": "Payment verified successfully"
                    }
                else:
                    return {"success": False, "message": "Payment verification failed"}
            else:
                return {"success": False, "message": "Verification request failed"}
                
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    async def create_order_summary(self, order_data):
        """Create order summary using LLM"""
        # Proper LLM initialization
        llm = ChatGroq(
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model_name="llama-3.1-70b-versatile",
            temperature=0.3
        )
        
        # Use proper async method
        summary = await llm.ainvoke(
            ORDER_SUMMARY_PROMPT.format(
                customer_name=order_data.get('customer_name', 'Customer'),
                phone_number=order_data.get('phone_number', 'N/A'),
                location=order_data.get('location', 'N/A'),
                order_items=order_data.get('order_items', 'N/A'),
                special_instructions=order_data.get('special_instructions', 'None')
            )
        )
        
        return summary.content
    
    async def send_twilio_notification(self, order_data, payment_data):
        """Send WhatsApp notification to owner"""
        try:
            # Create notification message using LLM
            llm = ChatGroq(
                groq_api_key=os.getenv("GROQ_API_KEY"),
                model_name="llama-3.1-70b-versatile",
                temperature=0.3
            )
            
            notification_msg = await llm.ainvoke(
                TWILIO_NOTIFICATION_PROMPT.format(
                    customer_name=order_data.get('customer_name', 'Customer'),
                    phone_number=order_data.get('phone_number', 'N/A'),
                    location=order_data.get('location', 'N/A'),
                    order_items=order_data.get('order_items', 'N/A'),
                    special_instructions=order_data.get('special_instructions', 'None'),
                    order_total=order_data.get('order_total', '0'),
                    payment_status=payment_data.get('status', 'confirmed')
                )
            )
            
            # Send WhatsApp message
            message = self.twilio_client.messages.create(
                body=notification_msg.content,
                from_=os.getenv('TWILIO_WHATSAPP_FROM'),
                to=os.getenv('OWNER_PHONE_NUMBER')
            )
            
            return message.sid
            
        except Exception as e:
            print(f"Twilio notification failed: {str(e)}")
            return None

# Global payment handler instance
payment_handler = PaymentHandler()