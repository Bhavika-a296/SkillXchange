"""Force reload the model in the running Django server"""
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from api.utils_safe import get_model

@require_http_methods(["POST"])
def reload_model(request):
    """Force reload the BERT model"""
    try:
        model = get_model(force_reload=True)
        if model:
            return JsonResponse({"status": "success", "message": "Model reloaded successfully"})
        else:
            return JsonResponse({"status": "error", "message": "Model failed to load"}, status=500)
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)
