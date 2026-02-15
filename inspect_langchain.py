import sys
import os

try:
    import langchain
    print(f"langchain path: {langchain.__file__}")
    print(f"langchain version: {getattr(langchain, '__version__', 'unknown')}")
    print(f"langchain dir: {dir(langchain)}")
    
    try:
        import langchain.chains
        print("langchain.chains imported successfully")
    except ImportError as e:
        print(f"Failed to import langchain.chains: {e}")

    import langchain_community
    print(f"langchain_community path: {langchain_community.__file__}")
        
except Exception as e:
    print(f"Error: {e}")
