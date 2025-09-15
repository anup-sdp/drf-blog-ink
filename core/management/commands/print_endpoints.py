# core/management/commands/print_endpoints.py
# run from project root: python manage.py print_endpoints
import os
import django
from django.core.management.base import BaseCommand
from django.urls import get_resolver


class Command(BaseCommand):
    help = 'Print all API endpoints'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('API Endpoints:'))
        self.stdout.write('=' * 50)
        
        # Get URL patterns
        resolver = get_resolver()
        self.print_urls(resolver.url_patterns, prefix='')
        
    def print_urls(self, urlpatterns, prefix=''):
        for pattern in urlpatterns:
            if hasattr(pattern, 'url_patterns'):
                # This is an include() - recurse into it
                new_prefix = prefix + str(pattern.pattern)
                self.print_urls(pattern.url_patterns, new_prefix)
            else:
                # This is a regular URL pattern
                url = prefix + str(pattern.pattern)
                # Clean up the URL for display
                url = url.replace('^', '').replace('$', '')
                
                # Get the view name
                if hasattr(pattern, 'callback'):
                    if hasattr(pattern.callback, 'cls'):
                        view_name = f"{pattern.callback.cls.__name__}"
                        # Get HTTP methods if it's a DRF view
                        if hasattr(pattern.callback.cls, 'http_method_names'):
                            methods = []
                            for method in ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']:
                                method_lower = method.lower()
                                if (hasattr(pattern.callback.cls, method_lower) and 
                                    method_lower in pattern.callback.cls.http_method_names):
                                    methods.append(method)
                            if methods:
                                view_name += f" [{', '.join(methods)}]"
                    else:
                        view_name = pattern.callback.__name__
                else:
                    view_name = "Unknown"
                
                # Format and print
                #full_url = f"http://127.0.0.1:8000/{url}"
                full_url = f"{url}"
                self.stdout.write(f"{full_url:<50} -> {view_name}")