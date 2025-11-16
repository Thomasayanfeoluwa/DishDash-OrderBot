from langchain_pinecone import PineconeVectorStore
from dotenv import load_dotenv
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from pinecone.grpc import PineconeGRPC as Pinecone
from datasets import load_dataset
from pinecone import ServerlessSpec
import pandas as pd
import os

# Read API key from environment variable
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
if PINECONE_API_KEY is None:
    raise ValueError("PINECONE_API_KEY environment variable is not set.")



try:
    dataset_dishes = load_dataset("Nnobody/Nigerian-Dishes")
    df_dishes= pd.DataFrame(dataset_dishes["train"])
    print("\nSuccessfully loaded Nnobody/Nigerian-Dishes")
except Exception as e:
    print(f"Error loading Nnobody/Nigerian-Dishes: {e}")



# Combine all relevant text columns into one string per row for chunking
texts_to_chunk = [
    f"Food Name: {row['Food_Name']}. Main Ingredients: {row['Main_Ingredients']}. Description: {row['Description']}. Health Benefits: {row['Food_Health']}. Class: {row['Food_Class']}. Region: {row['Region']}" 
    for index, row in df_dishes.iterrows()
]

# Function to chunk the texts
def chunk_texts_for_rag(texts):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    text_chunks = text_splitter.create_documents(texts)
    return text_chunks

# Execute the function
dish_chunks = chunk_texts_for_rag(texts_to_chunk)


def download_gugging_face_embeddings():
    embeddings= HuggingFaceEmbeddings(model_name = "sentence-transformers/all-MiniLM-L6-v2")
    return embeddings

embeddings = download_gugging_face_embeddings()


# Initialize client
pc = Pinecone(api_key=PINECONE_API_KEY)

index_name = "dashdishorderbot"
vector_dimension = 384 
metric_type = "cosine"

# Check whether the index exists
if not pc.has_index(name=index_name):
    pc.create_index(
        name=index_name,
        dimension=vector_dimension,
        metric=metric_type,
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )

# To get the index object later:
index = pc.Index(index_name)


docsearch = PineconeVectorStore.from_documents(
    documents= dish_chunks,
    index_name = index_name,
    embedding= embeddings
)


# # Use the API key explicitly
# llm = ChatGroq(
#     model="llama-3.1-70b-versatile",
#     temperature=0.4,
#     groq_api_key=GROQ_API_KEY
# )