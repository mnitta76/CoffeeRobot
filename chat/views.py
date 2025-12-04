import environ
import json
import os
import openai
from pathlib import Path
import requests

from langchain.document_loaders import PyPDFLoader
from langchain.vectorstores import Chroma, FAISS, Pinecone
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.chains import ConversationalRetrievalChain
from langchain.text_splitter import CharacterTextSplitter

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from blog.views import get_popular_posts, get_post_stats, trigger_blog_generation
from common.file_utils import upload_file_to_local, delete_file_from_local, delete_folder_from_local
from chat.forms import ChatForm
from chat.models import ChatMessage
from .models import RetrievalDocument, VECTORSTROE_FOLDER_NAME

BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env()
env.read_env(str(BASE_DIR / '.env'))

class ChromaCompatibleEmbedding:
    def __init__(self):
        self.embedder = OpenAIEmbeddings()

    def __call__(self, input):
        # For Chroma native API compatibility
        return self.embedder.embed_documents(input)

    def embed_documents(self, texts):
        # For LangChain Chroma compatibility
        return self.embedder.embed_documents(texts)

    def embed_query(self, text):
        # Optional but used in some contexts
        return self.embedder.embed_query(text)

@login_required
def chat(request):
    reply = ""
    selected_model = request.GET.get("model_choice", "gpt-3.5-turbo")
    response_mode = request.GET.get("response_mode", "chroma")
    messages = ChatMessage.objects.filter(user=request.user, response_mode=response_mode).order_by("timestamp")
    document = RetrievalDocument.objects.filter(response_mode=response_mode).first()
    file_name = ""
    if document:
        file_name = document.source_document_name

    retriever = get_retriever(response_mode)

    if request.method == "POST":
        form = ChatForm(request.POST)
        if form.is_valid():
            user_message = form.cleaned_data["message"]

            # ▼▼▼ ここからブログコマンド対応 ▼▼▼
            # /blog-top
            if user_message.startswith("/blog-top"):
                rows = get_popular_posts(days=7)
                reply = "\n".join(
                    [f"{i + 1}位: {r['slug']}（{r['count']}ビュー）" for i, r in enumerate(rows)]
                ) if rows else "直近7日間の閲覧データがありません。"

                ChatMessage.objects.create(user=request.user, role='assistant', content=reply,
                                           response_mode=response_mode)
                return redirect(f"{request.path}?model_choice={selected_model}&response_mode={response_mode}")

            # /blog-stats <slug>
            if user_message.startswith("/blog-stats "):
                slug = user_message[len("/blog-stats "):].strip()
                c7 = get_post_stats(slug, days=7)
                c30 = get_post_stats(slug, days=30)
                reply = f"記事 `{slug}` の閲覧数:\n- 直近7日: {c7}\n- 直近30日: {c30}"

                ChatMessage.objects.create(user=request.user, role='assistant', content=reply,
                                           response_mode=response_mode)
                return redirect(f"{request.path}?model_choice={selected_model}&response_mode={response_mode}")

            # /blog "テーマ"
            if user_message.startswith("/blog "):
                topic = user_message[len("/blog "):].strip().strip('"')
                reply = trigger_blog_generation(topic)

                ChatMessage.objects.create(user=request.user, role='assistant', content=reply,
                                           response_mode=response_mode)
                return redirect(f"{request.path}?model_choice={selected_model}&response_mode={response_mode}")
            # ▲▲▲ ここまでブログコマンド対応 ▲▲▲

            selected_model = request.POST.get("model_choice") or "gpt-3.5-turbo"
            response_mode = request.POST.get("response_mode") or 'chroma'
            retriever = get_retriever(response_mode)

            query = user_message
            if retriever:
                llm = ChatOpenAI(temperature=0, model_name=selected_model)
                chat_history = [
                    (msg.role, msg.content)
                    for msg in
                    ChatMessage.objects.filter(user=request.user, response_mode=response_mode).order_by("timestamp")
                ]
                qa_chain = ConversationalRetrievalChain.from_llm(
                    llm=llm,
                    retriever=retriever,
                    return_source_documents=True
                )
                result = qa_chain({
                    "question": user_message,
                    "chat_history": chat_history
                })
                reply = result["answer"]
            else:
                messages_for_api = []
                messages_for_api.append({'role': 'user', 'content': query})

                # GPT 応答生成
                openai.api_key = env.str('OPENAI_API_KEY')
                response = openai.ChatCompletion.create(model=selected_model, messages=messages_for_api)
                reply = response.choices[0]["message"]["content"].strip()

            # ユーザーメッセージ保存
            ChatMessage.objects.create(user=request.user, role='user', content=user_message, response_mode=response_mode)
            # アシスタント応答保存
            ChatMessage.objects.create(user=request.user, role='assistant', content=reply, response_mode=response_mode)

            return redirect(f"{request.path}?model_choice={selected_model}&response_mode={response_mode}")
    else:
        form = ChatForm(request.GET)
        messages = ChatMessage.objects.filter(user=request.user, response_mode=response_mode).order_by("timestamp")

    return render(request, "chat/top.html", {
        "form": form,
        "selected_model": selected_model,
        "response_mode": response_mode,
        "messages": messages,
        "pdf_file_name": file_name
    })

@require_POST
@login_required
def clear_chat(request):
    try:
        body = json.loads(request.body)
        mode = body.get("response_mode", "chroma")  # デフォルトは 'chroma'

        # 指定された response_mode に該当するユーザーの履歴だけ削除
        ChatMessage.objects.filter(user=request.user, response_mode=mode).delete()

        # アップロードされたPDFファイルを削除
        document = RetrievalDocument.objects.filter(response_mode=mode).first()
        file_name = ""
        if document:
            file_name = document.source_document_name
        if file_name != "":
            delete_file_from_local(file_name, request.user, f"{mode}/{VECTORSTROE_FOLDER_NAME}/", filename_prefix="chat")
        RetrievalDocument.objects.filter(response_mode=mode).delete()

        return JsonResponse({'status': 'cleared'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


def get_retriever(response_mode):
    """
    response_mode に対応する Retriever を取得する関数
    """
    try:
        # モデルからドキュメント情報を取得
        document = RetrievalDocument.objects.get(response_mode=response_mode)
        embedding = OpenAIEmbeddings()

        # ログで確認
        print(f"使用するベクトルストア: {document.vectorstore_name}")
        print(f"元のドキュメント名: {document.source_document_name}")

        # ベクトルストアの種類に応じて処理を切り替える
        if document.vectorstore_name == 'chroma':
            vectorstore = Chroma(persist_directory=document.vectorstore_path, embedding_function=embedding)
        elif document.vectorstore_name == 'faiss':
            vectorstore = FAISS.load_local(document.vectorstore_path, embeddings=embedding)
        elif document.vectorstore_name == 'pinecone':
            import pinecone
            pinecone.init(api_key='YOUR_API_KEY')
            vectorstore = Pinecone.from_existing_index(document.vectorstore_path, embedding_function=embedding)
        else:
            raise ValueError("対応していないベクトルストアです。")

        return vectorstore.as_retriever()

    except RetrievalDocument.DoesNotExist:
        print("対応するベクトルストアが見つかりません")
        return None

@require_POST
def set_retriever(request):
    """
    ベクトルストアの登録処理
    - ローカルに保存してベクトル化
    - DBに保存
    """
    response_mode = request.POST.get("response_mode")
    save_file_path = f"{response_mode}/{VECTORSTROE_FOLDER_NAME}/"

    # S3へのアップロードを先に行う
    upload_response = upload_file(request, save_file_path)
    if "error" in upload_response.content.decode():
        return JsonResponse({"error": "ローカルへのアップロードに失敗しました"}, status=500)

    # アップロード結果の解析
    upload_data = json.loads(upload_response.content)
    filename = upload_data.get("filename")
    file_path = upload_data.get("file_path")

    # LangChain のベクトル化処理
    try:
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        split_docs = text_splitter.split_documents(documents)
        # ベクトル化と永続化
        vectorstore_path = os.path.join(settings.MEDIA_ROOT, f"chat/{request.user}/{save_file_path}/")
        embedding = OpenAIEmbeddings()
        vectorstore = None
        if response_mode == 'chroma':
            print("★chroma")
            vectorstore = Chroma.from_documents(split_docs, embedding, persist_directory=vectorstore_path)
        elif response_mode == 'faiss':
            print("★FAISS")
            vectorstore = FAISS.load_local(vectorstore_path, embeddings=embedding, allow_dangerous_deserialization=True)
        elif response_mode == 'pinecone':
            print("★pinecone")
            import pinecone
            pinecone.init(api_key='YOUR_API_KEY')
            vectorstore = Pinecone.from_existing_index(vectorstore_path, embedding_function=embedding)
        else:
            raise ValueError("対応していないベクトルストアです。")

        vectorstore.persist()
        print("★３")
    except Exception as e:
        print(e)
        return JsonResponse({"error": f"ベクトルストアの生成に失敗しました: {str(e)}"}, status=500)

    print("★５")
    # データベースに保存
    RetrievalDocument.objects.update_or_create(
        response_mode=response_mode,
        defaults={
            'vectorstore_name': 'chroma',
            'vectorstore_path': vectorstore_path,
            'source_document_name': filename,
            'description': f'{response_mode}用のベクトルストア'
        }
    )

    # 成功メッセージ
    return JsonResponse({
        "message": f"{response_mode} のベクトルストアが作成されました。",
        "file_path": file_path,
        "file_name": filename,
        "local_path": vectorstore_path
    })

@require_POST
@login_required
def change_mode(request):
    print("change_mode")
    if request.method == "POST":
        form = ChatForm(request.POST)
        body = json.loads(request.body)
        selected_model = body.get("model_choice", "gpt-3.5-turbo")
        response_mode = body.get("response_mode", "chroma")
        messages = ChatMessage.objects.filter(user=request.user, response_mode=response_mode).order_by("timestamp")
        # メッセージをJSON形式に整形
        message_data = [{"role": msg.role, "content": msg.content} for msg in messages]

        document = RetrievalDocument.objects.filter(response_mode=response_mode).first()
        file_name = ""
        if document:
            file_name = document.source_document_name

        return JsonResponse({
            "messages": message_data,
            "selected_model": selected_model,
            "response_mode": response_mode,
            "file_name": file_name,
        })

    return JsonResponse({"error": "Invalid request"}, status=400)

@login_required
@require_POST
def upload_file(request, save_file_path=""):
    file = request.FILES.get("pdf")
    if not file:
        return JsonResponse({"error": "ファイルがありません"}, status=400)

    response = upload_file_to_local(file, request.user, save_file_path, filename_prefix="chat")

    return JsonResponse({
        "message": "finish: upload_file",
        "filename": response.get("filename"),
        "file_path": response.get("local_file_path")
    })