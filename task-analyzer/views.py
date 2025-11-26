# tasks/views.py
import json
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from scoring import score_tasks, detect_cycles
import os
from django.conf import settings

# Helper: normalize incoming payload to list of tasks
def _load_tasks_from_body(body_bytes):
    try:
        payload = json.loads(body_bytes.decode("utf-8"))
    except Exception:
        return None, "Invalid JSON payload"

    # Accept either {"tasks": [...], "strategy": "..."} or a raw list
    if isinstance(payload, dict) and "tasks" in payload:
        tasks = payload.get("tasks", [])
        strategy = payload.get("strategy", "smart")
    elif isinstance(payload, list):
        tasks = payload
        strategy = "smart"
    elif isinstance(payload, dict):
        # Single-task object: wrap into list
        tasks = [payload]
        strategy = payload.get("strategy", "smart")
    else:
        return None, "JSON must be a list or an object with 'tasks'"

    if not isinstance(tasks, list):
        return None, "'tasks' must be a list"

    return {"tasks": tasks, "strategy": strategy}, None


@csrf_exempt
@require_http_methods(["POST"])
def analyze_tasks(request):
    """
    POST /api/tasks/analyze/
    Body: JSON array of tasks OR {"tasks":[...], "strategy":"smart"}
    Response: { "tasks": [ ...scored tasks... ], "cycle_detected": bool, "cycles": [...] }
    """
    payload, err = _load_tasks_from_body(request.body)
    if err:
        return HttpResponseBadRequest(json.dumps({"error": err}), content_type="application/json")

    tasks = payload["tasks"]
    strategy = payload.get("strategy", "smart")

    # Ensure all tasks have stable ids (the scorer will assign if needed)
    # Detect cycles
    has_cycle, cycles = detect_cycles(tasks)

    # Score tasks
    try:
        scored = score_tasks(tasks, strategy=strategy)
    except Exception as e:
        return JsonResponse({"error": "Scoring failed", "details": str(e)}, status=500)

    return JsonResponse({"tasks": scored, "cycle_detected": has_cycle, "cycles": cycles}, safe=False)


@require_http_methods(["GET"])
def suggest_tasks(request):
    """
    GET /api/tasks/suggest/?tasks=<json-encoded-list>&strategy=smart
    Returns top 3 suggestions with a basic explanation in 'why'.
    Example usage (curl): 
      curl --get --data-urlencode 'tasks=[{"id":"1","title":"A","due_date":"2025-11-30",...}]' "http://localhost:8000/api/tasks/suggest/"
    """
    tasks_param = request.GET.get("tasks")
    if not tasks_param:
        return HttpResponseBadRequest(json.dumps({"error": "Provide 'tasks' query parameter (JSON-encoded list)"}), content_type="application/json")

    try:
        tasks = json.loads(tasks_param)
    except Exception:
        return HttpResponseBadRequest(json.dumps({"error": "Invalid JSON in 'tasks' parameter"}), content_type="application/json")

    strategy = request.GET.get("strategy", "smart")
    scored = score_tasks(tasks, strategy=strategy)
    top3 = scored[:3]

    # Provide a brief "why" message for each suggestion
    suggestions = []
    for t in top3:
        reasons = []
        comp = t.get("components", {})
        if comp.get("urgency", 0) >= 0.7:
            reasons.append("Urgent")
        if comp.get("importance_norm", 0) >= 0.7:
            reasons.append("High importance")
        if comp.get("effort", 0) >= 0.5:
            reasons.append("Quick win")
        if t.get("raw_score", 0) >= 0.9:
            reasons.append("High combined score")
        why = "; ".join(reasons) if reasons else "Top priority by selected strategy"
        suggestions.append({
            "id": t.get("id"),
            "title": t.get("title"),
            "score": t.get("score"),
            "why": why,
            "due_date": t.get("due_date")
        })

    return JsonResponse({"suggestions": suggestions}, safe=False)


def serve_index(request):
    """Serve the frontend `index.html` file located in project root."""
    index_path = os.path.join(settings.BASE_DIR, "index.html")
    if not os.path.exists(index_path):
        return HttpResponse("index.html not found", status=404)
    return FileResponse(open(index_path, "rb"), content_type="text/html")


def favicon(request):
    """Serve favicon.ico if present in project root; otherwise return 204 No Content."""
    fav_path = os.path.join(settings.BASE_DIR, "favicon.ico")
    if not os.path.exists(fav_path):
        return HttpResponse(status=204)
    return FileResponse(open(fav_path, "rb"), content_type="image/x-icon")


def serve_asset(request, filename):
    """Serve a handful of top-level static assets from project root safely.

    Only allow whitelisted filenames to avoid exposing arbitrary files.
    """
    allowed = {
        "script.js": "application/javascript",
        "styles.css": "text/css",
        "tasks.json": "application/json",
    }
    if filename not in allowed:
        return HttpResponse(status=404)

    asset_path = os.path.join(settings.BASE_DIR, filename)
    if not os.path.exists(asset_path):
        return HttpResponse(status=404)

    return FileResponse(open(asset_path, "rb"), content_type=allowed[filename])
