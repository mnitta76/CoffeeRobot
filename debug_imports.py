import sys
print("Starting imports...")

try:
    print("Importing langchain_community.document_loaders...")
    from langchain_community.document_loaders import PyPDFLoader
    print("PyPDFLoader imported.")

    print("Importing langchain_community.vectorstores...")
    from langchain_community.vectorstores import Chroma, FAISS, Pinecone
    print("Vectorstores imported.")

    print("Importing langchain_community.embeddings...")
    from langchain_community.embeddings import OpenAIEmbeddings
    print("OpenAIEmbeddings imported.")

    print("Importing langchain_community.chat_models...")
    from langchain_community.chat_models import ChatOpenAI
    print("ChatOpenAI imported.")

    print("Importing langchain.chains...")
    from langchain.chains import RetrievalQA
    from langchain.chains import ConversationalRetrievalChain
    print("Chains imported.")

    print("Importing langchain.text_splitter...")
    from langchain.text_splitter import CharacterTextSplitter
    print("TextSplitter imported.")

    print("All imports successful.")
except Exception as e:
    print(f"Error during import: {e}")
except KeyboardInterrupt:
    print("Import interrupted.")
