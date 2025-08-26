# chat/choices.py

MODEL_CHOICES = [
    ("gpt-3.5-turbo", "GPT-3.5"),
    ("gpt-4", "GPT-4"),
]

RESPONSE_MODE_CHOICES = [
    ('chroma', 'Chroma'),
    ('faiss', 'FAISS'),
    ('pinecone', 'Pinecone')
]

ROLE_CHOICES = [
    ('user', 'User'),
    ('assistant', 'Assistant'),
]
