from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def api_root(request):
    return Response({
        "message": "Initial API Endpoint",
        "available_endpoints": {
            "main": "/api/main/",
        }
    })

