import requests
import json
from imports import paystack
from prompt import ORDER_SUMMARY_PROMPT, TWILIO_NOTIFICATION_PROMPT
import chainlit as cl

class PaymentHandler:
    def __init__(self):
        self.paystack_secret_key = os.getenv('PAYSTACK_SECRET_KEY')
        self.paystack_public_key = os.getenv('PAYSTACK_PUBLIC_KEY')
        self.base_url = "https://api.paystack.co"
    
    async def initialize_payment(self, email, amount, order_data, metadata=None):
        """Initialize Paystack payment"""
        try:
            # Convert amount to kobo (Paystack requires amount in kobo)
            amount_kobo = int(amount * 100)
            
            # Prepare payment data
            payment_data = {
                "email": email,
                "amount": amount_kobo,
                "currency": "NGN",
                "metadata": metadata or {},
                "callback_url": "https://your-domain.com/verify-payment"  # Update with your domain
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
        llm = ChatOpenAI(temperature=0.3)
        
        summary = await llm.apredict(
            text=ORDER_SUMMARY_PROMPT.format(
                customer_name=order_data.get('customer_name', 'Customer'),
                phone_number=order_data.get('phone_number', 'N/A'),
                location=order_data.get('location', 'N/A'),
                order_items=order_data.get('order_items', 'N/A'),
                special_instructions=order_data.get('special_instructions', 'None')
            )
        )
        
        return summary
    
    async def send_twilio_notification(self, order_data, payment_data):
        """Send WhatsApp notification to owner"""
        try:
            # Create notification message using LLM
            llm = ChatOpenAI(temperature=0.3)
            
            notification_msg = await llm.apredict(
                text=TWILIO_NOTIFICATION_PROMPT.format(
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
            message = twilio_client.messages.create(
                body=notification_msg,
                from_=os.getenv('TWILIO_WHATSAPP_FROM'),
                to=os.getenv('OWNER_PHONE_NUMBER')
            )
            
            return message.sid
            
        except Exception as e:
            print(f"Twilio notification failed: {str(e)}")
            return None

# Global payment handler instance
payment_handler = PaymentHandler()