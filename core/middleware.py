from django.contrib import messages
from django.shortcuts import redirect


class AuthenticationRedirectMiddleware:
    """
    Middleware que maneja las redirecciones de usuarios no autenticados
    y muestra mensajes informativos.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Procesa la vista antes de que se ejecute
        """
        # Si el usuario no está autenticado y está tratando de acceder a páginas protegidas
        if (not request.user.is_authenticated and 
            request.path.startswith('/calendario/') and 
            request.path not in ['/calendario/login/', '/calendario/register/']):
            
            messages.warning(request, 'Debes iniciar sesión para acceder a esta página.')
            # Guardar la URL a la que intentaba acceder
            request.session['next_url'] = request.get_full_path()
            return redirect('/calendario/login/')
        
        return None