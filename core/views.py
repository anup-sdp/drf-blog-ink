# core, views.py:
from django.shortcuts import render, redirect

# Create your views here.
def api_root_view(request):
    #return redirect('api-root')  # api-root is conflicting name here, as drf default router / djoser also uses it.
	return redirect('/api/v1/') # Direct URL redirect,