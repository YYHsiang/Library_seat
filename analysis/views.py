from django.shortcuts import render
from django.http import JsonResponse
from main.models import Location, Seat, Occupy_History

#rest framework
from rest_framework.views import APIView
from rest_framework.response import Response

def analysis(response):
    location_list = Location.objects.all()

    return render(response, "analysis/analysis.html", {"location_list": location_list})


class ChartData(APIView):
    authentication_classes = []
    permission_classes = []   

    def get(self, request, format=None):
        location_seat_cnt = []
        location = []

        location_list = Location.objects.all()
        for temp in location_list:
            location_seat_cnt.append(temp.seat_set.count())
            location.append(temp.name)

        data = {
            "location" : location ,
            "location_seat_cnt" : location_seat_cnt,
        }
        return Response(data)