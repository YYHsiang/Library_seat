from django.shortcuts import render
from django.http import JsonResponse
from main.models import Location, Seat, OccupyHistory

#rest framework
from rest_framework.views import APIView
from rest_framework.response import Response

# average
from datetime import timedelta
from django.db.models import Count, Avg
from django.db.models import F
import statistics

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
        location_average_time = location_average_occupy_time(location_list)

        for temp in location_list:
            location_seat_cnt.append(temp.seat_set.count())
            location.append(temp.name)

        data = {
            "location" : location ,
            "location_seat_cnt" : location_seat_cnt,
            "location_average_time": location_average_time,
        }
        return Response(data)


def location_average_occupy_time(Locations: list or tuple):
    location_avg_time = []
    for location in Locations:
        seats = location.seat_set.all()
        seat_avg_time = []
        for seat in seats:
            avg_time = Seat_Average_occupy_time(seat)
            #add secons data into list
            if avg_time is not None:
                seat_avg_time.append(avg_time)
        # caculate average occupy time in current location
        if seat_avg_time != []:
            location_avg_time.append(statistics.mean(seat_avg_time))
        else:
            location_avg_time.append(0)

    return location_avg_time

def Seat_Average_occupy_time(Seat):
    # caculate average occupy time of each seat in minutes
    avg_time = Seat.occupyhistory_set.all().aggregate(average_difference=Avg(F('end_time') - F('start_time')))
    if avg_time['average_difference'] is not None:
        avg_time_min =(avg_time['average_difference'].seconds//60)%60
    else:
        avg_time_min = None

    return avg_time_min