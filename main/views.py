from django.shortcuts import render
from .models import Camera_Data, Location, Seat, Occupy_History
from ip_camera.models import Camera
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
        camera_name = response.POST.get('camera',0)
        floor = (response.POST.get('location',0))
        occupy = response.POST.get('occupy',0)

        seat_temp = Seat.objects.filter(seat_number= seat_number)
        camera_temp = Camera.objects.filter(name= camera_name)
        print(seat_temp)
        print(camera_temp)
        # check if Seat is already exist
        if seat_temp is None:
            print("Seat doesnt exist")
        elif camera_temp is None:
            print("Camera doesnt exist")
        else:
            # create camera_data and add it to relate seat
            c_data = Camera_Data()
            c_data.camera = Camera.objects.get(name= camera_name)
            c_data.occupy = occupy
            c_data.save()
            print("new Camera data: " + str(c_data))

            #check new camera send data to current seat
            if seat_temp.camera.count() == 0:
                seat_temp.camera.add(camera_temp)
                seat_temp.save()
                print("new camera added")
            elif camera_temp not in seat_temp.camera.all():
                seat_temp.camera.add(camera_temp)
                seat_temp.save()
                print("new camera added")

            # add data to current Seat
            ifnew = False
            for data in seat_temp.camera_data.all():
                print("Seat data" + str(data))
                if data.camera == camera_temp:
                    ifnew = False
                    pass
                else:
                    ifnew = True

                if ifnew:
                    seat_temp.camera_data.add(c_data)
                    seat_temp.save()

            #check full camera data
            occupy_count = 0
            if len(seat_temp.camera_data.all()) == len(seat_temp.camera.all()):
                for data in seat_temp.camera_data.all():
                    if data.occupy >= "1":
                        occupy_count += 1

                # majority decision
                if occupy_count > len(seat_temp.camera.all())/2 :
                    seat_temp.occupy = True
                else:
                    seat_temp.occupy = False

                seat_temp.camera_data.clear()
                seat_temp.save()

        '''#remove same seat_number
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
        s.save()'''

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
    