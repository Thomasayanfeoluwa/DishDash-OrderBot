from langchain_core.prompts import ChatPromptTemplate

# Main RAG prompt for dish recommendations
RAG_PROMPT = PromptTemplate(
    template="""You are DishDash OrderBot, a helpful assistant for Nigerian food delivery.

Use the following context about Nigerian dishes to answer the question. If you don't know the answer based on the context, say so.

Context: {context}

Question: {question}

Please provide:
1. Dish recommendations based on the query
2. Description of the dishes
3. Typical preparation time if available
4. Suggestions for complementary dishes

Answer:""",
    input_variables=["context", "question"]
)

# Order summary prompt
ORDER_SUMMARY_PROMPT = PromptTemplate(
    template="""Create a clear order summary for the following order:

Customer: {customer_name}
Phone: {phone_number}
Location: {location}
Order Items: {order_items}
Special Instructions: {special_instructions}

Please format the order as:
📦 ORDER SUMMARY
👤 Customer: {customer_name}
📞 Phone: {phone_number}
📍 Location: {location}
🍽️ Items: {order_items}
📝 Instructions: {special_instructions}

Make it professional and easy to read.""",
    input_variables=["customer_name", "phone_number", "location", "order_items", "special_instructions"]
)

# Twilio notification prompt
TWILIO_NOTIFICATION_PROMPT = PromptTemplate(
    template="""🚨 NEW ORDER ALERT 🚨

Customer: {customer_name}
Phone: {phone_number}
Location: {location}

Order Details:
{order_items}

Special Instructions: {special_instructions}

Order Total: ₦{order_total}
Payment Status: {payment_status}

Please prepare this order immediately!""",
    input_variables=["customer_name", "phone_number", "location", "order_items", "special_instructions", "order_total", "payment_status"]
)