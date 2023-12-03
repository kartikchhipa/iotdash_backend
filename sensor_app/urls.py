from django.urls import path, include
from .views import SensorDataAPI, DeviceAPI, DeviceAllocationAPI, LiveDataAPI, UserLogsAPI, UserInteractionAPI, get_session_id, addSensorAPI

urlpatterns = [
    path('deviceAllocation/', DeviceAllocationAPI.as_view()),
    path('sensorData/', SensorDataAPI.as_view()),
    path('addSensor/', addSensorAPI.as_view() ),
    path('devices/', DeviceAPI.as_view()),
    path('liveData/', LiveDataAPI.as_view()),
    path('userLogs/', UserLogsAPI.as_view()),
    path('userInteraction/', UserInteractionAPI.as_view()),    
    path('get_session_id/', get_session_id, name='get_session_id'),

]


# path('sensorDataAPI/', SensorAPIView.as_view()),
# path('locationDataAPI/', LocationAPIView.as_view()),
# path('liveSensorData/', LiveSensorAPIView.as_view()),
# path('device/', DeviceAPIView.as_view()),
# path('getUserLogs/', UserLogsAPIView.as_view()),
# path('getUserInteraction/', UserInteractionAPIView.as_view()),
# path('getDevice/', GetDeviceAPI.as_view()),

# path('getsensorData/', getSensorData.as_view() )