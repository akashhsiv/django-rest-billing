from django.urls import get_resolver, NoReverseMatch
from rest_framework.reverse import reverse  
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def api_root(request, format=None):
    reverse_dict = get_resolver().reverse_dict
    response_data = {}
    named_routes = [name for name in reverse_dict if isinstance(name, str)]

    for name in sorted(named_routes):
        try:
            if name == "user-detail":
                url = reverse(name, kwargs={'pk': 1}, request=request, format=format)
            else:
                url = reverse(name, request=request, format=format)

            response_data[name] = url  # ✅ always set it here
        except NoReverseMatch as e:
            response_data[name] = f"Error: {str(e)}"
        except Exception as e:
            response_data[name] = f"Error: {str(e)}"

    return Response(response_data)
