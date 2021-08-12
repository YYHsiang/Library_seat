from django.shortcuts import render
from .models import Location, Seat

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

def create(response):
    print(response.POST.get('seat',0));
    if response.method == "POST":
        s = Seat()
        floor = Location.objects.get(name="1F")
        s.location = floor
        s.seat_number=1
        s.seat_position_x =10
        s.seat_position_y =20
        s.occupy=True
        s.save()
    