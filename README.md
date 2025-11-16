# DishDash-OrderBot

# End-to-end-DishDash-OrderBot-Generative-AI


# How to run?
### STEPS:

Clone the repository

```bash
Project repo: https://github.com/Thomasayanfeoluwa/DishDash-OrderBot.git
```
### STEP 01- Create a conda environment after opening the repository

```bash
conda create -n Carebot python=3.10 -y
```

```bash
conda activate Carebot
```


### STEP 02- install the requirements
```bash
pip install -r requirements.txt
```


### Create a `.env` file in the root directory and add your Pinecone & openai credentials as follows:

```ini
PINECONE_API_KEY = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
OPENAI_API_KEY = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
TWILIO_ACCOUNT_SID = "***************************"
TWILIO_AUTHENTICATION_TOKEN = "xxxxxxxxxxxxxxxxxxxxxxxxx"
TWILIO_WHATSAPP_FROM  = "xxxxxxxxxxxxxxxxxxxxxxxxx"
OWNER_WHATSAPP_NUMBER = "xxxxxxxxxxxxxxxxxxxxxxxx"
PAYSTACK_SECRET_KEY = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
PAYSTACK_PUBLIC_SECRECT_KEY = "xxxxxxxxxxxxxxxxxxxxxxxxxxxx"
GROQ_API_KEY="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
PINECONE_API_KEY="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```


```bash
# run the following command to store embeddings to pinecone
python store_index.py
```

```bash
# Finally run the following command
python app.py
```

Now,
```bash
open up localhost:
```


### Techstack Used:

- Python
- LangChain
- Chainlit
- Groq
- Pinecone
- Paystack
- Twilio


### System Architecture Overview

┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend        │    │   External      │
│   (Chainlit)    │◄──►│   Components     │◄──►│   Services      │
│                 │    │                  │    │                 │
│ • Chat UI       │    │ • RAG System     │    │ • Pinecone      │
│ • User Input    │    │ • Order Manager  │    │ • OpenAI        │
│ • Payment Flow  │    │ • Payment Handler│    │ • Paystack      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │                         │
                              │                         │
                              ▼                         ▼
                    ┌──────────────────┐    ┌─────────────────┐
                    │   Data Flow      │    │ Notifications   │
                    │                  │    │                 │
                    │ • Session Mgmt   │    │ • Twilio WhatsApp│
                    │ • Order State    │    │ • Owner Alerts  │
                    └──────────────────┘    └─────────────────┘


# Detailed Component Architecture

1. Frontend Layer (Chainlit)
┌─────────────────────────────────────────────────┐
│                Chainlit App                     │
├─────────────────────────────────────────────────┤
│  • User Session Management                      │
│  • Chat Interface                               │
│  • Action Handlers (Buttons)                    │
│  • Message Routing                              │
└─────────────────────────────────────────────────┘
                         │
                         │ Handles user interactions
                         ▼                    

2. Backend Core Components
┌─────────────────────────────────────────────────┐
│               Core System                        │
├─────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │   RAG       │  │   Order     │  │  Payment    │ │
│  │   System    │  │  Manager    │  │  Handler    │ │
│  └─────────────┘  └─────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────┘
         │                 │                 │
         │                 │                 │
         ▼                 ▼                 ▼

3. RAG System Architecture
┌─────────────────────────────────────────────────┐
│                  RAG System                      │
├─────────────────────────────────────────────────┤
│  User Query → Pinecone Vector Store → LLM → Response │
│                                                  │
│  Components:                                     │
│  • OpenAI Embeddings                            │
│  • Pinecone Index                               │
│  • RetrievalQA Chain                            │
│  • Prompt Templates                             │
└─────────────────────────────────────────────────┘


4. Order Management Flow
┌─────────────────────────────────────────────────┐
│              Order Manager                       │
├─────────────────────────────────────────────────┤
│  1. Collect Customer Info                       │
│     - Phone Number                              │
│     - Location                                  │
│     - Instructions                              │
│                                                  │
│  2. Manage Cart                                 │
│     - Add Items                                 │
│     - Calculate Total                           │
│     - Order ID Generation                       │
│                                                  │
│  3. Coordinate Payment                          │
│     - Initiate Paystack                         │
│     - Verify Payment                            │
│     - Update Order Status                       │
└─────────────────────────────────────────────────┘



5. Payment Integration Architecture
┌─────────────────────────────────────────────────┐
│              Payment Handler                     │
├─────────────────────────────────────────────────┤
│  ┌─────────────┐        ┌─────────────┐         │
│  │  Paystack   │◄──────►│  Twilio     │         │
│  │ Integration │        │  WhatsApp   │         │
│  └─────────────┘        └─────────────┘         │
│         │                       │               │
│         ▼                       ▼               │
│  • Initialize Payment    • Send Notification    │
│  • Verify Transaction    • Order Alert          │
│  • Handle Callbacks                            │
└─────────────────────────────────────────────────┘


# Complete Data Flow

### Phase 1: User Onboarding & Dish Discovery

User → Chainlit → RAG System → Nigerian Dishes Database
     ↓
User gets dish recommendations
     ↓
User selects items for order

### Phase 2: Order Collection
User provides:
1. Phone Number → Session Storage
2. Location → Session Storage  
3. Instructions → Session Storage
     ↓
Order Manager creates:
• Order ID
• Cart Items
• Total Calculation

### Phase 3: Payment Processing
Order Manager → Payment Handler → Paystack API
                              ↓
User receives payment link ← Paystack Response
                              ↓
User completes payment → Paystack Webhook
                              ↓
Payment Handler verifies transaction

### Phase 4: Notification & Confirmation
Payment Handler → Twilio API → Owner WhatsApp
                    ↓
Order Manager → User Confirmation
                    ↓
System clears cart & resets state



### Session Management Architecture
┌─────────────────────────────────────────────────┐
│              User Session State                  │
├─────────────────────────────────────────────────┤
│  • qa_chain: RAG system instance                │
│  • order_cart: [] - current items               │
│  • customer_info: {} - phone, location, etc.    │
│  • order_stage: "welcome" | "collecting_phone"  │
│                 | "collecting_location"         │
│                 | "collecting_instructions"     │
│                 | "ready"                       │
│  • current_order: {} - active order data        │
│  • payment_reference: "" - Paystack reference   │
└─────────────────────────────────────────────────┘



# API Integration Flow

### Paystack Integration

1. Initialize Payment:
   Order Data → Payment Handler → Paystack API → Payment URL

2. User Payment:
   User ← Payment URL → Paystack ← Payment Completion

3. Verification:
   Payment Handler → Paystack Verify API → Payment Status

4. Completion:
   Success → Update Order → Send Notification
   Failure → Error Message → Retry Flow

### Twilio Integration
1. Order Confirmation:
   Payment Success → Order Data → Twilio API

2. Message Formatting:
   Order Details → LLM Formatting → WhatsApp Message

3. Delivery:
   Twilio → Owner WhatsApp Number → Order Alert


### Error Handling Architecture
┌─────────────────────────────────────────────────┐
│              Error Handling                      │
├─────────────────────────────────────────────────┤
│  • API Connection Errors                        │
│  • Payment Verification Failures                │
│  • Session Timeout Handling                     │
│  • Invalid User Input Management                │
│  • Retry Mechanisms for Failed Payments         │
└─────────────────────────────────────────────────┘


### State Transition Diagram
┌───────────┐    Order    ┌─────────────┐    Payment   ┌─────────────┐
│  Welcome  │────────────►│ Collecting  │─────────────►│  Payment    │
│   State   │             │ Customer    │             │  Processing │
└───────────┘             │   Info      │             └─────────────┘
                              │                             │
                              │                             │
                              ▼                             ▼
                      ┌─────────────┐    Success    ┌─────────────┐
                      │   Ready     │◄──────────────│ Completion  │
                      │   State     │               │   & Notify  │
                      └─────────────┘               └─────────────┘