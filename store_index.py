from langchain_pinecone import PineconeVectorStore
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from pinecone.grpc import PineconeGRPC as Pinecone
from datasets import load_dataset
from pinecone import ServerlessSpec
import pandas as pd
import os


load_dotenv()

# Read API key from environment variable
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
if PINECONE_API_KEY is None:
    raise ValueError("PINECONE_API_KEY environment variable is not set.")

def setup_pinecone_index():
    """Run this function once to set up your Pinecone index"""
    
    # Load dataset
    try:
        dataset_dishes = load_dataset("Nnobody/Nigerian-Dishes")
        df_dishes = pd.DataFrame(dataset_dishes["train"])
        print("\nSuccessfully loaded Nnobody/Nigerian-Dishes")
    except Exception as e:
        print(f"Error loading Nnobody/Nigerian-Dishes: {e}")
        return

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

    # Initialize embeddings
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

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
        print(f"Created new index: {index_name}")
    else:
        print(f"Index {index_name} already exists")

    # Populate the index
    print("Populating Pinecone index with dish data...")
    docsearch = PineconeVectorStore.from_documents(
        documents=dish_chunks,
        index_name=index_name,
        embedding=embeddings
    )
    print("✅ Pinecone index populated successfully!")
    
    return docsearch

if __name__ == "__main__":
    # Run this script once to set up your index
    setup_pinecone_index()