import os
from datetime import timedelta

import requests
from django.db.models import Sum
from django.utils import timezone

from .models import BlogView


# ---------------------------------------------------------
# ① GitHub Actions をトリガーしてブログ生成を開始する
# ---------------------------------------------------------
def trigger_blog_generation(topic: str) -> str:
    """
    GitHub Actions workflow_dispatch に topic を渡して
    ブログ生成を開始する
    """
    token = os.getenv("GITHUB_TOKEN")
    owner = os.getenv("GITHUB_OWNER")
    repo = os.getenv("GITHUB_REPO")

    if not token or not owner or not repo:
        return "環境変数(GITHUB_TOKEN / OWNER / REPO)が設定されていません"

    url = (
        f"https://api.github.com/repos/{owner}/{repo}/actions/"
        f"workflows/blog-auto.yml/dispatches"
    )

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
    }

    payload = {
        "ref": "main",
        "inputs": {
            "topic": topic
        }
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 204:
        return f"ブログ生成を開始しました！\nトピック: {topic}"
    else:
        return (
            "ブログ生成の開始に失敗しました。\n"
            f"status={response.status_code}\n"
            f"message={response.text}"
        )


# ---------------------------------------------------------
# ② 人気記事（トップ N）を集計する
# ---------------------------------------------------------
def get_popular_posts(days: int = 7, limit: int = 3):
    """
    過去 N 日間の閲覧データから人気記事 TOP N を返す
    """
    since = timezone.now() - timedelta(days=days)

    qs = (
        BlogView.objects.filter(created_at__gte=since)
        .values("slug")
        .annotate(count=Sum("count"))
        .order_by("-count")[:limit]
    )

    return list(qs)


# ---------------------------------------------------------
# ③ 特定記事の閲覧数を集計
# ---------------------------------------------------------
def get_post_stats(slug: str, days: int = 30) -> int:
    """
    指定 slug の記事について、過去 N 日間の閲覧数を返す
    """
    since = timezone.now() - timedelta(days=days)
    stats = BlogView.objects.filter(
        slug=slug,
        created_at__gte=since
    ).aggregate(total=Sum("count"))
    return stats.get("total") or 0

