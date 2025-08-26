from django.db import models
from django.contrib.auth.models import User
from .choices import RESPONSE_MODE_CHOICES, ROLE_CHOICES

VECTORSTORE_CHOICES = [
    ('chroma', 'Chroma'),
    ('faiss', 'FAISS'),
    ('pinecone', 'Pinecone')
]

VECTORSTROE_FOLDER_NAME = "vectorstore"

class ChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    response_mode = models.CharField(max_length=15, choices=RESPONSE_MODE_CHOICES, default='free', blank=True)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.role}: {self.content[:30]}"

    def is_chroma(self):
        return self.response_mode == 'chroma'

    def is_faiss(self):
        return self.response_mode == 'faiss'

    def is_pinecone(self):
        return self.response_mode == 'pinecone'

class RetrievalDocument(models.Model):
    """
    各 response_mode に対応するベクトルストアとドキュメントの情報
    """
    response_mode = models.CharField(max_length=15, choices=RESPONSE_MODE_CHOICES, unique=True)
    vectorstore_name = models.CharField(max_length=15, choices=VECTORSTORE_CHOICES, default='chroma')
    vectorstore_path = models.CharField(max_length=255)  # ベクトルストアのパス
    source_document_name = models.CharField(max_length=255)  # 元のドキュメントの名前
    description = models.TextField(blank=True, null=True)  # 任意の説明文
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.response_mode} - {self.source_document_name}"