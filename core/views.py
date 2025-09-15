# core, views.py:
from django.shortcuts import render, redirect

# Create your views here.
def api_root_view(request):
    #return redirect('api-root')  # api-root is conflicting name here, as drf default router / djoser also uses it.
	return redirect('/api/v1/') # Direct URL redirect,

# core/views.py
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

# import the DRF function-based views (they are decorated with @api_view)
from payment import views as payment_views


def _api_path(path: str) -> str:
    """
    Build the api path. Use BACKEND_URL in production if you prefer absolute URLs.
    Default is a relative path which works locally and on deployed host.
    """
    # Use relative api path to avoid hardcoding host; change to use settings.BACKEND_URL if needed.
    return f"/api/v1/payment/{path}/"


@csrf_exempt
def payment_success_redirect(request):
    """
    If POST -> forward the request to the DRF api view so payload is preserved.
    If GET  -> redirect browser to the /api/v1/... URL (useful for manual testing).
    """
    if request.method == "POST":
        # Directly call the DRF view callable (it accepts Django request)
        return payment_views.payment_success(request)
    # For browser GET, redirect to the API route (or use full URL via settings.BACKEND_URL)
    return HttpResponseRedirect(_api_path("success"))


@csrf_exempt
def payment_fail_redirect(request):
    if request.method == "POST":
        return payment_views.payment_fail(request)
    return HttpResponseRedirect(_api_path("fail"))


@csrf_exempt
def payment_cancel_redirect(request):
    if request.method == "POST":
        return payment_views.payment_cancel(request)
    return HttpResponseRedirect(_api_path("cancel"))
