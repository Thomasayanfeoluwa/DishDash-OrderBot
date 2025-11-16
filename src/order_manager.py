import chainlit as cl
from payment_handler import payment_handler
import json
from datetime import datetime

class OrderManager:
    def __init__(self):
        self.orders = {}
    
    async def create_order(self, user_session, order_items, customer_info):
        """Create a new order"""
        order_id = f"DD{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        order_data = {
            "order_id": order_id,
            "items": order_items,
            "customer_info": customer_info,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "total_amount": self.calculate_total(order_items)
        }
        
        self.orders[order_id] = order_data
        user_session.set("current_order", order_data)
        
        return order_data
    
    def calculate_total(self, order_items):
        """Calculate order total (simplified - you'd have actual prices)"""
        # This is a simplified calculation
        # In reality, you'd fetch prices from your database
        base_price = len(order_items) * 1500  # Assuming average dish price
        return base_price
    
    async def process_payment(self, order_data, user_session):
        """Process payment for order"""
        try:
            # Initialize payment
            payment_result = await payment_handler.initialize_payment(
                email=order_data["customer_info"].get("email", "customer@dishdash.com"),
                amount=order_data["total_amount"],
                order_data=order_data,
                metadata={
                    "order_id": order_data["order_id"],
                    "customer_phone": order_data["customer_info"].get("phone"),
                    "customer_name": order_data["customer_info"].get("name", "Customer")
                }
            )
            
            if payment_result["success"]:
                # Store payment reference in session
                user_session.set("payment_reference", payment_result["reference"])
                
                # Send payment link to user
                actions = [
                    cl.Action(
                        name="pay_now", 
                        value=payment_result["reference"],
                        label="💳 Pay Now"
                    ),
                    cl.Action(
                        name="verify_payment",
                        value=payment_result["reference"],
                        label="✅ Verify Payment"
                    )
                ]
                
                await cl.Message(
                    content=f"""💰 **Payment Required**

Order Total: ₦{order_data['total_amount']:,.2f}

Please click the button below to complete your payment:""",
                    actions=actions
                ).send()
                
                return True
            else:
                await cl.Message(
                    content=f"❌ Payment initialization failed: {payment_result['message']}"
                ).send()
                return False
                
        except Exception as e:
            await cl.Message(
                content=f"❌ Payment processing error: {str(e)}"
            ).send()
            return False
    
    async def verify_and_complete_order(self, reference, user_session):
        """Verify payment and complete order"""
        verification = await payment_handler.verify_payment(reference)
        
        if verification["success"]:
            order_data = user_session.get("current_order")
            
            # Update order status
            order_data["status"] = "confirmed"
            order_data["payment_reference"] = reference
            order_data["paid_at"] = datetime.now().isoformat()
            
            # Send Twilio notification
            await payment_handler.send_twilio_notification(
                order_data=order_data,
                payment_data=verification["data"]
            )
            
            # Create order summary
            summary = await payment_handler.create_order_summary({
                "customer_name": order_data["customer_info"].get("name", "Customer"),
                "phone_number": order_data["customer_info"].get("phone", "N/A"),
                "location": order_data["customer_info"].get("location", "N/A"),
                "order_items": ", ".join(order_data["items"]),
                "special_instructions": order_data["customer_info"].get("instructions", "None"),
                "order_total": order_data["total_amount"]
            })
            
            # Clear cart
            user_session.set("order_cart", [])
            
            await cl.Message(
                content=f"""🎉 **Order Confirmed!** 🎉

{summary}

📱 You will receive a confirmation message shortly.
⏱️ Your food will be delivered within 30-45 minutes.

Thank you for choosing DishDash!"""
            ).send()
            
            return True
        else:
            await cl.Message(
                content=f"❌ Payment verification failed: {verification['message']}"
            ).send()
            return False

# Global order manager instance
order_manager = OrderManager()