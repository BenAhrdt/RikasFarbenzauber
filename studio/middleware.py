class SecurityHeaders:
    def __init__(self, get_response):
        self.get_response = get_response
    def __call__(self, request):
        response = self.get_response(request)
        response["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' blob: data:; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'"
        response["Referrer-Policy"] = "same-origin"
        return response


class UploadLimit:
    """Reject oversized requests before CSRF parses multipart data."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        from django.http import JsonResponse
        if request.path == '/api/photos/' and request.method == 'POST':
            try:
                length = int(request.META.get('CONTENT_LENGTH') or 0)
            except ValueError:
                return JsonResponse({'error': 'Ungültiger Upload.'}, status=400)
            if length > 13 * 1024 * 1024:
                return JsonResponse({'error': 'Bitte ein Foto mit höchstens 12 MB wählen.'}, status=413)
        return self.get_response(request)
