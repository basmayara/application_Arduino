from .models import Dht11
from .serializers import DHT11serialize
from .alerts import notify_if_alert
from rest_framework.decorators import api_view
from rest_framework import generics
from rest_framework.response import Response


@api_view(["GET"])
def Dlist(request):
    all_data = Dht11.objects.all()
    data = DHT11serialize(all_data, many=True).data
    return Response({"data": data})


class Dhtviews(generics.CreateAPIView):
    queryset = Dht11.objects.all()
    serializer_class = DHT11serialize

    def perform_create(self, serializer):
        obj = serializer.save()
        notify_if_alert(obj.temperature, obj.humidity)