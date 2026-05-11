from django.conf import settings
from django.http import FileResponse, HttpResponseNotFound
from django.urls import include, path, re_path

INDEX_FILE = settings.FRONTEND_DIST / "index.html"


def serve_index(_request, *_args, **_kwargs):
    if not INDEX_FILE.exists():
        return HttpResponseNotFound(
            "Frontend not built. Run `npm run build` inside frontend/."
        )
    return FileResponse(open(INDEX_FILE, "rb"), content_type="text/html")


urlpatterns = [
    path("api/", include("calendar_app.urls")),
    re_path(r"^.*$", serve_index),
]
