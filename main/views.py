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
    if response.method == "POST":
        seat_number=response.POST.get('seat',0)
        floor = (response.POST.get('location',0))
        occupy = response.POST.get('occupy',0)

        rows = Seat.objects.filter(seat_number=seat_number)
        for r in rows: 
            r.delete() 

        s = Seat()
        s.location = Location.objects.get(name=floor)
        s.seat_number=seat_number
        s.seat_position_x =0
        s.seat_position_y =0
        if occupy >"0":
            s.occupy=True
        else:
            s.occupy=False
        s.save()
        
    