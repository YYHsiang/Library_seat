from django.shortcuts import render
from .models import Location

# Create your views here.
def  home(response):
    location_list = Location.objects.all()
    return render(response, "main/base.html", {"location_list":location_list})

def location(response, location_name):
    location_list = Location.objects.all()
    try:
        location = Location.objects.get(name=location_name)
        
        #count the available seats
        available_seat=0
        for seat in location.seat_set.all():
            if seat.occupy == False:
                available_seat +=1

        return render(response, "main/location.html", { "location_list":location_list, "location":location, "available_seat":available_seat})

    except Location.DoesNotExist:
        return render(response, "main/error_404.html", {})