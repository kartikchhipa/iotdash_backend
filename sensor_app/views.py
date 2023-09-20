from django.shortcuts import render
from .serializers import SensorSerializer, LiveSensorSerializer, LocationSerializer, UserLogsSerializer, UserInteractionSerializer, DeviceSerializer, DeviceAllocationSerializer
from .models import Sensor, Location, LiveSensor, User, UserLogs, UserInteraction, Devices, DeviceAllocation
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from django.http import HttpResponse
import ast
import random
import requests
from decouple import config
import datetime
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from django.views.decorators.csrf import csrf_exempt
import itertools
from django.http import JsonResponse



def get_session_id(request):
    session_id = request.session.session_key
    return JsonResponse({'session_id': session_id})


class SensorDataAPI(APIView):

    def get(self, request):
        user = request.user

        # if the user is AnonymousUser then return empty list
        if(user.is_anonymous):
            return Response([], status=status.HTTP_200_OK)
        
        elif(user.is_staff):
            sensors = Sensor.objects.all()
            sensor_serialized = SensorSerializer(sensors, many=True).data
            return Response(sensor_serialized, status=status.HTTP_200_OK)
            
        else:
            device = DeviceAllocation.objects.filter(user = user)
            if(device.exists()):

                # select all the devices allocated to the user
                device_allocation = device.all()
                sensor_serialized = []
                for device in device_allocation:

                    # select all the sensors of the device
                    sensors = Sensor.objects.filter(device_id = device.device.device_id)
                    print(sensors)
                    sensor_serialized.append(SensorSerializer(sensors, many=True).data)

                flat_list = list(itertools.chain(*sensor_serialized))
                return Response(flat_list, status=status.HTTP_200_OK)
            
            else:
                return Response([], status=status.HTTP_200_OK)
        
    @csrf_exempt
    def delete(self, request):
        
        user = request.user
        if(user.is_staff):
            data = request.data
            sensor_id = data["sensor_id"]
            sensor = Sensor.objects.filter(sensor_id=sensor_id)
            if (sensor.exists()):
                req_sensor = sensor.first()
                req_sensor.delete()
                return Response({"Success": "Sensor Deleted Successfully"}, status=status.HTTP_200_OK)
            
            return Response({"Error": "No Sensor found with ID"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"Error": "You are not authorized to perform this action"}, status=status.HTTP_400_BAD_REQUEST)

class DeviceAPI(APIView):

    def get(self,request):

        user = request.user
        if(user.is_anonymous):
            return Response([], status=status.HTTP_200_OK)
        
        elif(user.is_staff):
            devices = Devices.objects.all()
            device_serialized = DeviceSerializer(devices, many=True).data
            return Response(device_serialized, status=status.HTTP_200_OK)
        
        else:
            devices = DeviceAllocation.objects.filter(user = user)
            device_serialized = []
            if(devices.exists()):
                for dev in devices:
                    device = Devices.objects.filter(device_id = dev.device.device_id)
                    device_serialized.append(DeviceSerializer(device, many=True).data)
                flat_list = list(itertools.chain(*device_serialized))
                return Response(flat_list, status=status.HTTP_200_OK)
        
    def delete(self, request):
        user = request.user 
        if(user.is_staff):
            data = request.data
            device_id = data["device_id"]
            device = Devices.objects.filter(device_id=device_id)
            if (device.exists()):
                req_device = device.first()
                req_device.delete()
                return Response({"Success": "Device Deleted Successfully"}, status=status.HTTP_200_OK)
            
            return Response({"Error": "No Device found with ID"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"Error": "You are not authorized to perform this action"}, status=status.HTTP_400_BAD_REQUEST)
        
    def put(self, request):
        user = request.user
        device_id = request.data["device_id"]
        if(user.is_staff):
            devices = Devices.objects.filter(device_id=device_id)
            if (devices.exists()):
                device = devices.first()
                device.device_name = request.data["device_name"]
                device.save()
                return Response({"Success": "Device Updated Successfully"}, status=status.HTTP_200_OK)
            else:
                return Response({"Error": "No Device found with ID"}, status=status.HTTP_400_BAD_REQUEST)
                
    def post(self,request,format=None):
        data = request.data
        device_id = data["device_id"]
        if Devices.objects.filter(device_id=device_id).exists():
            return Response({"Error": "Device already exists"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            device = Devices(device_id=device_id, device_name=data["device_name"])
            device.save()
            return Response({"Success": "Device added succesfully"}, status=status.HTTP_200_OK)

class DeviceAllocationAPI(APIView):

    def get(self , request):

        user = request.user
        if(user.is_anonymous):
            return Response([], status=status.HTTP_200_OK)
        
        elif(user.is_staff):
            device_allocation = DeviceAllocation.objects.all()
            device_allocation_serialized = DeviceAllocationSerializer(device_allocation, many=True).data
            return Response(device_allocation_serialized, status=status.HTTP_200_OK)
        
        else:
            device_allocation = DeviceAllocation.objects.filter(user = user)
            device_allocation_serialized = DeviceAllocationSerializer(device_allocation, many=True).data
            return Response(device_allocation_serialized, status=status.HTTP_200_OK)
    
    def post(self ,request,format=None):

        user = request.user
        if(user.is_staff):
            data = request.data
            device_id = data["device_id"]
            userID = data["userID"]

            user1 = User.objects.filter(id=userID).first()
            if Devices.objects.filter(device_id = device_id).exists():
                device = Devices.objects.filter(device_id = device_id).first()
                if(DeviceAllocation.objects.filter(device=device, user=user1).exists()):
                    return Response({"Error": "Device already allocated to this user"}, status=status.HTTP_400_BAD_REQUEST)
                device_allocation = DeviceAllocation(device=device, user=user1, username=user1.name)
                device_allocation.save()
                return Response({"Success": "Device allocated succesfully"}, status=status.HTTP_200_OK)
            else:
                return Response({"Error": "Device does not exists"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"Error": "You are not authorized to perform this action"}, status=status.HTTP_400_BAD_REQUEST)
        
    def delete(self, request):

        data = request.data
        user = request.user
        device_id = data["device_id"]
        if(user.is_staff):
            device = Devices.objects.filter(device_id = device_id)
            if (device.exists()):
                req_allocation = DeviceAllocation.objects.filter(device=device.first())
                if(req_allocation.exists()):
                    for allocation in req_allocation:
                        allocation.delete()
                    return Response({"Success": "Device allocation deleted succesfully"}, status=status.HTTP_200_OK)
                else:
                    return Response({"Error": "No allocation found with this device"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"Error": "No Device found with ID"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"Error": "You are not authorized to perform this action"}, status=status.HTTP_400_BAD_REQUEST)
        
    def put(self, request):
        user = request.user
        data = request.data
        if(user.is_staff):
            device_id = data["device_id"]
            userID = data["userID"]
            user = User.objects.filter(id=userID)
            if(user.exists()):
                user = user.first()
                device_allocation = DeviceAllocation.objects.filter(user=user).first()
                device_allocation.user = user
                device_allocation.save()
                return Response({"Success": "Device allocation updated succesfully"}, status=status.HTTP_200_OK)
            else:
                return Response({"Error": "User does not exists"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"Error": "You are not authorized to perform this action"}, status=status.HTTP_400_BAD_REQUEST)
                
class LiveDataAPI(APIView):
    live_sensor_serializer_class = LiveSensorSerializer

    def get(self, request):
        return Response({"Success": "Get the data"}, status=status.HTTP_200_OK)

    def post(self, request):
        print(request.content_type)
        request_text = request.body.decode('utf-8')
        print(request_text)

        res = request.data
        
        
        data = res['Data']
        
        sensor_id = res['sensor_id']
        
        device_id = res['device_id']
        timestamp = str(datetime.datetime.now())
        sensor = Sensor.objects.filter(sensor_id=sensor_id, device_id = device_id)
        if (sensor.exists()):
            req_sensor = sensor.first()
            livedata = LiveSensor(sensor=req_sensor, data=data, timestamp=timestamp, device_id=device_id)
            livedata.save()
            return Response({"Success": "Data Added Successfully"}, status=status.HTTP_200_OK)
        else:
            return Response({"Error": "No Sensor found with these credentials"}, status=status.HTTP_400_BAD_REQUEST)





class UserLogsAPI(APIView):
    # Get all user logs
    def get(self, request):
        all_userlogs = UserLogs.objects.order_by('-timestamp')
        userlogs_serialized = UserLogsSerializer(all_userlogs, many=True).data
        # Marking all previously sent logs
        for log in all_userlogs:
            log.isSeen = True
            log.save()
        return Response(userlogs_serialized, status=status.HTTP_200_OK)

    # Post the logs
    def post(self, request):
        user = request.user
        data = request.data
        log = UserLogs(userName=user.name, data=data['data'])
        log.save()
        return Response({"Success": "Logs saved succesfully"}, status=status.HTTP_200_OK)
    

class UserInteractionAPI(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        user = request.user
        print(user.name)
        if UserInteraction.objects.filter(date=datetime.date.today()).exists():
            obj = UserInteraction.objects.filter(date=datetime.date.today()).first()
            time = obj.time
            time = int(time) + 5
            obj.time = str(time)
            obj.save()
        else:
            obj = UserInteraction(user=user, time="0")
            obj.save()
        return Response({"Success": "Get the data"}, status=status.HTTP_200_OK)

        all_userlogs = UserLogs.objects.order_by('-timestamp')
        userlogs_serialized = UserLogsSerializer(all_userlogs, many=True).data
        # Marking all previously sent logs
        for log in all_userlogs:
            log.isSeen = True
            log.save()
        return Response(userlogs_serialized, status=status.HTTP_200_OK)
    
    def get(self, request):
        user_interaction = UserInteraction.objects.filter(user=request.user).all()
        user_interaction_serialized = UserInteractionSerializer(user_interaction, many=True).data
        return Response(user_interaction_serialized, status=status.HTTP_200_OK)
    


# class GetSensorAPIView(APIView):
#     sensor_serializer_class = SensorSerializer
#     # Get a particular sensor

#     def post(self, request, format=None):
#         data = request.data
#         sensor_id = data["sensor_id"] 
#         if (Sensor.objects.filter(sensor_id=sensor_id).exists()):
#             req_sensor = Sensor.objects.filter(sensor_id=sensor_id).first()
#             return Response(req_sensor, status=status.HTTP_200_OK)
#         return Response({"Error": "No Sensor found with these credentials"}, status=status.HTTP_400_BAD_REQUEST)




# class SensorAPIView(APIView):
#     sensor_serializer_class = SensorSerializer
#     def get(self, request, format=None):
        
        
#         all_sensors = Sensor.objects.all()
#         stu_serialized = SensorSerializer(all_sensors, many=True)
#         json_object = JSONRenderer().render(stu_serialized.data)
#         return HttpResponse(json_object, content_type="application/Json")
    

#     # def delete(self, request,sensor_id, format=None):
       
#     #     print(sensor_id)
#     #     if sensor_id:
#     #         try:
#     #             req_sensor = Sensor.objects.get(sensor_id=sensor_id)
#     #             req_sensor.delete()
#     #             return HttpResponse("Success: Sensor Deleted Successfully", status=status.HTTP_200_OK)
#     #         except Sensor.DoesNotExist:
#     #             return HttpResponse("No Sensor found with this ID", status=status.HTTP_400_BAD_REQUEST)
#     #     else:
#     #         return HttpResponse("Missing sensor_id in request data", status=status.HTTP_400_BAD_REQUEST)
        

#     def delete(self, request):
#         print(request)
#         data = request.data
#         sensor_id = data["sensor_id"]
#         print(request)
#         if (Sensor.objects.filter(sensor_id=sensor_id).exists()):
#             req_sensor = Sensor.objects.filter(sensor_id=sensor_id).first()
#             req_sensor.delete()
#             return HttpResponse("Success: Sensor Deleted Successfully", status=status.HTTP_200_OK)
#         return HttpResponse("No Sensor found with this ID", status=status.HTTP_400_BAD_REQUEST)

#     # API to add/update a new sensor
#     def post(self, request, format=None):
#         data = request.data
#         name = data['name']
#         id = data['sensor_id']
#         unit = data['unit']
#         locationID = data['locationID']

#         # Checking the exixting of a sensor
#         if Sensor.objects.filter(sensor_id=id).exists():
#             if (Location.objects.filter(locId=locationID).exists()):
#                 location = Location.objects.filter(locId=locationID).first()
#                 sensor = Sensor.objects.filter(sensor_id=id).first()
#                 sensor.location = location
#                 sensor.name = name
#                 sensor.unit = unit
#                 sensor.save()
#                 return Response("Data Updated Succesfully", status=status.HTTP_200_OK)
#             else:
#                 return Response("No Location found with this ID", status=status.HTTP_400_BAD_REQUEST)
#         else:
#             # Check locationID is correct or not
#             if (Location.objects.filter(locId=locationID).exists()):
#                 location = Location.objects.filter(locId=locationID).first()
#                 sensor = Sensor(location=location, name=name,
#                                 sensor_id=id, unit=unit)
#                 sensor.save()
#                 return Response("Sensor added succesfully", status=status.HTTP_200_OK)
#             else:
#                 print("No Location found with this ID")
#                 return Response("No Location found with this ID", status=status.HTTP_400_BAD_REQUEST)

#     # API to update the sensor data

#     def put(self, request, format=None):
#         data = request.data
#         sensor_serializer = self.sensor_serializer_class(data=data)
#         if sensor_serializer.is_valid():
#             sensor_serializer.save()
#             return Response(sensor_serializer, status=status.HTTP_200_OK)
#         else:
#             return Response(sensor_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class LocationAPIView(APIView):
#     location_serializer_class = LocationSerializer
#     permission_classes = [IsAuthenticated]
#     # Get all locations

#     def get(self, request, format=None):
        
#         user = request.user
        
        
#         all_locations = []
#         if user.is_staff is True:
#             all_locations = Location.objects.all()
#             print(all_locations)
#         else:
#             all_locations = Location.objects.filter(user=user)
#         loc_serialized = LocationSerializer(all_locations, many=True).data
#         return Response(loc_serialized, status=status.HTTP_200_OK)

#     # Delete the location
#     def delete(self, request, format=None):
#         data = request.data
#         print(data)
#         location_id = data["location_id"]
        
#         if (Location.objects.filter(locId=location_id).exists()):
#             req_location = Location.objects.filter(
#                 locId=location_id).first()
#             req_location.delete()
#             return Response("Location Deleted Succesfully", status=status.HTTP_200_OK)
#         return Response("No Location found with this ID", status=status.HTTP_400_BAD_REQUEST)

#     # API to update the location data
#     def put(self, request, format=None):
#         data = request.data
#         sensor_serializer = self.sensor_serializer_class(data=data)
#         if sensor_serializer.is_valid():
#             sensor_serializer.save()
#             return Response(sensor_serializer, status=status.HTTP_200_OK)
#         else:
#             return Response(sensor_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class DeviceAPIView(APIView):
#     # API to get all devices
#     def get(self, request):
#         all_devices = Location.objects.all()
#         devices_serialized = LocationSerializer(all_devices, many=True).data
#         return Response(devices_serialized, status=status.HTTP_200_OK)

#     # API to add a new device

#     def post(self, request, format=None):
#         data = request.data
#         userId = data["user"]
#         deviceName = data["name"]
#         deviceID = data["deviceID"]
#         user = User.objects.filter(id=userId).first()
#         device = Location(user=user, name=deviceName, deviceID=deviceID)
#         device.save()
#         return Response({"Success"}, status=status.HTTP_200_OK)