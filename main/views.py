from django.http import HttpResponse
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

        #count the available seats
        available_seat=0
        for seat in location.seat_set.all():
            if seat.occupy == False:
                available_seat +=1

        return render(response, "main/location.html", { "location_list":location_list, "location":location, "available_seat": available_seat})

    except Location.DoesNotExist:
        return render(response, "main/error_404.html", {})

def create(response):
    if response.method == "POST":
        #obtain request data
        seat_number=response.POST.get('seat',0)
        camera_name = response.POST.get('camera',0)
        floor = response.POST.get('location',0)
        occupy = int(response.POST.get('occupy',0))

        seat_temp = Seat.objects.get(seat_number= seat_number)
        camera_temp = Camera.objects.get(name= camera_name)
        print("seat_number: "+seat_number+", camera_name: "+camera_name+", occupy:"+str(occupy))
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

            #check new camera send data to current seat
            if camera_temp not in seat_temp.camera.all():
                seat_temp.camera.add(camera_temp)
                seat_temp.save()
                print("new camera added")

            # add data to current Seat
            ifnew = False
            if not seat_temp.camera_data.all().exists():
                seat_temp.camera_data.add(c_data)
            else:
                for data in seat_temp.camera_data.all():
                    # remove old data from same camera
                    if data.camera == camera_temp:
                        data.delete()
                    seat_temp.camera_data.add(c_data)
            #print(seat_temp.camera_data.all())

            #check full camera data
            occupy_count = 0
            print("camera_data_number: "+str(seat_temp.camera_data.all().count()))
            if seat_temp.camera_data.all().count() == seat_temp.camera.all().count():
                for data in seat_temp.camera_data.all():
                    if data.occupy >= 1:
                        occupy_count += 1

                # majority decision
                if occupy_count > len(seat_temp.camera.all())/2 :
                    seat_temp.occupy = True
                    print("seat_number: " + str(seat_temp.seat_number) + " occupy: " + str(seat_temp.occupy))
                else:
                    seat_temp.occupy = False
                seat_temp.save()
                
                #seat_temp.camera_data.clear()
                data = Camera_Data.objects.all()
                data.delete()
                print(seat_temp.occupy)
                

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
        
    return HttpResponse('Mom, I am here!')