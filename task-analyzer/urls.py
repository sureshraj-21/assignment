"""URL Configuration for task-analyzer project."""
from django.urls import path
import views

urlpatterns = [
    path("", views.serve_index, name="index"),
    path("script.js", views.serve_asset, kwargs={"filename": "script.js"}),
    path("styles.css", views.serve_asset, kwargs={"filename": "styles.css"}),
    path("tasks.json", views.serve_asset, kwargs={"filename": "tasks.json"}),
    path("favicon.ico", views.favicon, name="favicon"),
    path("api/tasks/analyze/", views.analyze_tasks, name="tasks-analyze"),
    path("api/tasks/suggest/", views.suggest_tasks, name="tasks-suggest"),
]
