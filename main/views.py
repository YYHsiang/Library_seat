from django.shortcuts import render
from .models import Location, Seat, Occupy_History
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

# Create your views here.
def  home(response):
    location_list = Location.objects.all()
    return render(response, "main/base.html", {"location_list":location_list})

def location(response, location_name):
    location_list = Location.objects.all()
    try:
        location = Location.objects.get(name=location_name)

        return render(response, "main/location.html", { "location_list":location_list, "location":location})

    except Location.DoesNotExist:
        return render(response, "main/error_404.html", {})

def create(response):
    if response.method == "POST":
        #obtain request data
        seat_number=response.POST.get('seat',0)
        floor = (response.POST.get('location',0))
        occupy = response.POST.get('occupy',0)

        #remove same seat_number
        rows = Seat.objects.filter(seat_number=seat_number)
        for r in rows: 
            r.delete() 

        #add new seat_number item
        s = Seat()
        s.location = Location.objects.get(name=floor)
        s.seat_number=seat_number
        s.camera_number=0
        s.seat_position_x = (int(seat_number)%10) * 70
        s.seat_position_y = 0
        if occupy >"0":
            s.occupy=True
        else:
            s.occupy=False
        s.save()    

        #count the available seats
        location = Location.objects.get(name=floor)
        available_seat=0
        for seat in location.seat_set.all():
            if seat.occupy == False:
                available_seat +=1

        #send data to website
        layer = get_channel_layer()
        async_to_sync(layer.group_send)(
            'chat',
            {
                'type': 'available_seat',
                'available_seat': str(available_seat),
                'seat_number': seat_number,
                'occupy': str(occupy)
            }
        )
    