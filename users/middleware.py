from django.shortcuts import redirect
from django.conf import settings
from django.urls import reverse

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # List of paths that don't require authentication
        exempt_urls = [
            reverse('login'),  # Login page
            reverse('admin:index'),  # Admin index page
        ]
        
        # Check for static files and other exempt URLs
        if not request.user.is_authenticated:
            if not request.path.startswith(settings.STATIC_URL) and all(not request.path.startswith(url) for url in exempt_urls):
                return redirect('login')
        
        return self.get_response(request)
