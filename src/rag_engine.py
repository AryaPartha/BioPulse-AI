#import os
#from langchain.text_splitter import RecursiveCharacterTextSplitter
#from langchain_huggingface import HuggingFaceEmbeddings
#from langchain_groq import ChatGroq
#from langchain.chains import RetrievalQA
#from dotenv import load_dotenv
#
#load_dotenv()

# def process_fitness_pdf(file_path):
#     """Turns a PDF into a searchable vector knowledge base."""
#     # Load document
#     loader = PyPDFLoader(file_path)
#     documents = loader.load()
    
#     # Split into manageable chunks
#     text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
#     texts = text_splitter.split_documents(documents)
    
#     # Create free embeddings and store in FAISS
#     embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
#     vector_db = FAISS.from_documents(texts, embeddings)
#     return vector_db

# def ask_rag_ai(vector_db, query):
#     """Retrieves context from PDF and generates an answer via Groq."""
#     llm = ChatGroq(
#         groq_api_key=os.getenv("GROQ_API_KEY"), 
#         model_name="llama3-8b-8192"
#     )
    
#     qa_chain = RetrievalQA.from_chain_type(
#         llm=llm, 
#         chain_type="stuff", 
#         retriever=vector_db.as_retriever()
#     )
#     return qa_chain.run(query)