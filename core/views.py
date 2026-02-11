from django.shortcuts import render

# Create your views here.

def home(request):
    """Vista principal del sitio"""
    return render(request, 'core/home.html')
