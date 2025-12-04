from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

def redirect_to_login(request):
    return redirect('login')  # 'login' は accounts.urls 内で name='login' のURLを指す

urlpatterns = [
    path('', redirect_to_login, name='root_redirect'),
    path('accounts/', include('accounts.urls')),
    path('admin/', admin.site.urls),
    path('blog/', include("blog.urls")),
    path('chat/', include('chat.urls')),
    path('coffeenotes/', include('coffeenotes.urls')),
    path('taskrunner/', include('taskrunner.urls')),
]

# 開発環境でのみ有効
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)