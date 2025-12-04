import json
import os
from datetime import timedelta
from urllib.parse import urlparse

import requests
from django.conf import settings
from django.db.models import Sum
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from .models import BlogView


def _parse_date_from_path(value):
    if not value:
        return None

    parsed = urlparse(value)
    path = parsed.path if parsed.scheme else value
    segments = [seg for seg in path.strip("/").split("/") if seg]

    for idx in range(len(segments) - 2):
        y, m, d = segments[idx:idx + 3]
        if len(y) == 4 and y.isdigit() and m.isdigit() and d.isdigit():
            return int(y), int(m), int(d)
    return None


def _resolve_date_parts(payload, referrer, slug):
    now = timezone.localdate()
    year = payload.get("year")
    month = payload.get("month")
    day = payload.get("day")

    try:
        if year is not None and month is not None and day is not None:
            return int(year), int(month), int(day)
    except (TypeError, ValueError):
        pass

    for candidate in (referrer, slug):
        parts = _parse_date_from_path(candidate)
        if parts:
            return parts

    return now.year, now.month, now.day


def _record_view(slug, payload, referrer, user_agent):
    year, month, day = _resolve_date_parts(payload, referrer, slug)
    obj, created = BlogView.objects.get_or_create(
        slug=slug,
        year=year,
        month=month,
        day=day,
        defaults={
            "referrer": referrer,
            "user_agent": user_agent,
            "count": 1,
        },
    )
    if not created:
        obj.count += 1
        obj.referrer = referrer or obj.referrer
        obj.user_agent = user_agent or obj.user_agent
        obj.last_viewed = timezone.now()
        obj.save(update_fields=["count", "referrer", "user_agent", "last_viewed"])
    return obj

@csrf_exempt
def record_blog_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "invalid json"}, status=400)

    slug = data.get("slug")
    if not slug:
        return JsonResponse({"error": "slug is required"}, status=400)

    referrer = data.get("referrer") or request.META.get("HTTP_REFERER", "")
    user_agent = request.META.get("HTTP_USER_AGENT", "")
    _record_view(slug, data, referrer, user_agent)
    return JsonResponse({"status": "ok"})


@csrf_exempt
def trigger_blog_generation_view(request):
    """
    チャットから叩く用:
    POST /api/blog/generate/ { "topic": "コーヒー×AI" }
    """
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "invalid json"}, status=400)

    topic = data.get("topic", "")

    owner = settings.GITHUB_OWNER      # 'your-github-id'
    repo = settings.GITHUB_REPO        # 'astro-site-repo'
    workflow_file = "blog-auto.yml"    # workflows に置いたファイル名

    url = f"https://api.github.com/repos/{owner}/{repo}/actions/workflows/{workflow_file}/dispatches"

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {settings.GITHUB_TOKEN}",
    }

    payload = {
        "ref": "main",
        "inputs": {"topic": topic},
    }

    r = requests.post(url, headers=headers, json=payload, timeout=10)
    if r.status_code == 204:
        return JsonResponse({"status": "started", "topic": topic})
    return JsonResponse({"error": r.text}, status=r.status_code)


# 以下は Step4 用：チャットから使う集計ヘルパー

def get_popular_posts(days=7, limit=3):
    since = timezone.now() - timedelta(days=days)
    qs = (
        BlogView.objects.filter(created_at__gte=since)
        .values("slug")
        .annotate(count=Sum("count"))
        .order_by("-count")[:limit]
    )
    return list(qs)


def get_post_stats(slug, days=30):
    since = timezone.now() - timedelta(days=days)
    stats = BlogView.objects.filter(
        slug=slug, created_at__gte=since
    ).aggregate(total=Sum("count"))
    return stats.get("total") or 0

def trigger_blog_generation(topic):
    token = os.getenv("GITHUB_TOKEN")
    owner = os.getenv("GITHUB_OWNER")
    repo = os.getenv("GITHUB_REPO")

    url = f"https://api.github.com/repos/{owner}/{repo}/actions/workflows/blog-auto.yml/dispatches"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
    }
    payload = {"ref": "main", "inputs": {"topic": topic}}

    r = requests.post(url, headers=headers, json=payload)

    if r.status_code == 204:
        return f"ブログ生成を開始しました。\nトピック: {topic}"
    else:
        return f"生成開始に失敗しました: {r.status_code} {r.text}"

@csrf_exempt
def record_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    try:
        body = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"error": "invalid json"}, status=400)

    slug = body.get("slug")
    if not slug:
        return JsonResponse({"error": "slug required"}, status=400)

    referrer = body.get("referrer") or request.META.get("HTTP_REFERER", "")
    user_agent = request.META.get("HTTP_USER_AGENT", "")

    try:
        _record_view(slug, body, referrer, user_agent)
        return JsonResponse({"status": "ok"})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
