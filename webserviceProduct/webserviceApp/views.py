from rest_framework.response import Response
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework import status
from webserviceApp.models import ProviderService
from webserviceApp.serializers import BookinghistorySerializer, ProviderServiceSerializer, ServicereviewSerializer, UserSerializer
from bson import ObjectId
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from django.contrib.auth.hashers import check_password
from .models import BookingHistory, ServiceReview, User
from django.core.files.storage import default_storage
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.storage import default_storage
from rest_framework.parsers import MultiPartParser, FormParser
from django.utils.timezone import now
import datetime
from datetime import datetime, timedelta
from django.utils.timezone import now
from django.db import models
from datetime import datetime
from django.utils.timezone import localtime
from bson.decimal128 import Decimal128
from decimal import Decimal


#----------------------------- For Admin -----------------------------------# 


#For thr admin approval -  
@api_view(['PUT'])
@permission_classes([AllowAny])
def request_service_approval(request):
    service_id = request.data.get('service_id')
    status = request.data.get('status')

    try:
        service = ProviderService.objects.get(_id=ObjectId(service_id))
    except ProviderService.DoesNotExist:
        return Response({"error": "Service not found or already processed"}, status=404)

    #  Convert `Decimal128` to `Decimal` before using it
    if isinstance(service.price, Decimal128):  
        service.price = service.price.to_decimal()  

    #  Handle price updates properly
    if "price" in request.data:
        try:
            price_value = Decimal(request.data['price'])      # Convert string to Decimal
            service.price = price_value
        except (ValueError, TypeError):
            return Response({"error": "Invalid price format. Must be a valid decimal number."}, status=400)

    # Handle approval and rejection
    if status == "approve":
        service.status = "approved"
        service.save()
        return Response({"message": "Service approved successfully"}, status=200)

    elif status == "reject":
        service.status = "rejected"
        service.save()
        return Response({"message": "Service rejected"}, status=200)

    return Response({"error": "Invalid status"}, status=400)  # Handle invalid status




#------------------------- For Provider ---------------------------#


#For Creating New Services - 
@api_view(['POST'])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser, FormParser])
def create_service(request):
    serializer = ProviderServiceSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#For Get the Perticular Services -
@api_view(['POST'])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser, FormParser])
def get_service(request, _id):
    try:
        service = ProviderService.objects.get(_id=(ObjectId(_id)))
    except ProviderService.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = ProviderServiceSerializer(service)
    return Response(serializer.data)


#For Updatethe Services -
@api_view(['PUT'])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser, FormParser])
def update_service(request, _id):
    try:
        service = ProviderService.objects.get(_id=(ObjectId(_id)))
    except ProviderService.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    # Fetch old image and video paths
    old_image_path = service.image.name if service.image else None
    old_video_path = service.video.name if service.video else None

    # Parse incoming data
    new_image = request.FILES.get('image')
    new_video = request.FILES.get('video')

    # Compare and delete old image if a new one is uploaded and different
    if new_image and old_image_path and old_image_path != new_image.name:
        default_storage.delete(old_image_path)

    # Compare and delete old video if a new one is uploaded and different
    if new_video and old_video_path and old_video_path != new_video.name:
        default_storage.delete(old_video_path)

    serializer = ProviderServiceSerializer(service, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#For the Deleting the services -
@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_service(request, _id):
    try:
        service = ProviderService.objects.get(_id=(ObjectId(_id)))
    except ProviderService.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    # Delete associated media files before deleting the service entry
    if service.image:
        default_storage.delete(service.image.name)
    if service.video:
        default_storage.delete(service.video.name)

    service.delete()
    return Response({'message': "Deleted Data Successfully"}, status=status.HTTP_204_NO_CONTENT)


#For get the all Services -
@api_view(['POST'])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser, FormParser])
def list_services(request):
    services = ProviderService.objects.all()
    serializer = ProviderServiceSerializer(services, many=True)
    return Response(serializer.data)



#--------------------- For LogIn, New Register And LogOut ------------------------#


# Register a New User - 
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid(): 
        serializer.save()
        return Response({'message': "User registered successfully"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# Login a user -
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    selected_role = request.data.get('role')

    try:
        user = User.objects.get(username=username)
        
        if check_password(password, user.password):
            if selected_role == user.role:
                
                if user.role == 'admin':
                    panel = 'Admin Dashboard'
                elif user.role == 'provider':
                    panel = 'Provider Dashboard'
                elif user.role == 'client':
                    panel = 'Client Dashboard'
                else:
                    return Response({'error': 'Invalid role'}, status=status.HTTP_403_FORBIDDEN)
                
                return Response({
                    'message': 'Login successful',
                    'role': user.role,
                    'redirect_to': panel
                }, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Selected role does not match'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        
    except User.DoesNotExist:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)



# For logOut User -
@api_view(['POST'])
@permission_classes([AllowAny])
def logout(request):
    try:
        request.auth.delete()
        return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': 'Something went wrong during logout'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




# ---------------------------- For Client --------------------------------#


# For the search a perticular service -
@api_view(["GET"])
@permission_classes([AllowAny])
def search_services(request):
    query = request.GET.get("query", "").strip().lower()  # Convert to lowercase for consistency
    if not query:
        return Response({"error": "Please provide a search term"}, status=400)

    services = ProviderService.objects.filter(service_type=query)  # Exact match on service_type
    service_list = list(services.values())

    if not service_list:
        return Response({"message": "No matching services found"}, status=404)

    serializer = ProviderServiceSerializer(services, many=True)  # Serialize the queryset
    return Response({"services": serializer.data})



# For Booking A perticualr Services -
@api_view(["POST"])
@permission_classes([AllowAny])
def book_service(request):
    service_id = request.data.get("service_id")
    user_id = request.data.get("user_id")

    if not service_id or not user_id:
        return Response({"error": "Service ID and User ID are required"}, status=400)

    try:
        service = ProviderService.objects.get(_id=ObjectId(service_id))
    except ProviderService.DoesNotExist:
        return Response({"error": "Service not found"}, status=404)

    # Ensure we get the local server time for accurate comparison
    current_time = now().astimezone().time()
    print(f"Current server time: {current_time}")  # Debug log

    if service.time_slot:
        try:
            start_time_str, end_time_str = service.time_slot.split("-")
            start_time = datetime.strptime(start_time_str.strip(), "%H:%M").time()
            end_time = datetime.strptime(end_time_str.strip(), "%H:%M").time()

            print(f"Start Time: {start_time}, End Time: {end_time}")  # Debug log

            # Allow booking only within the exact range
            if not (start_time <= current_time <= end_time):
                return Response({
                    "error": f"Booking allowed only between {start_time_str} and {end_time_str}",
                    "status": 400
                })
        except ValueError:
            return Response({"error": "Invalid time slot format. Use HH:MM-HH:MM"}, status=400)

    # Save the booking request in the BookingHistory model
    BookingHistory.objects.create(
        user_id=user_id,
        service_name=service.name,
        service_type=service.service_type
    )

    return Response({"message": "Booking request has been successfully submitted."}, status=201)


# For Client Histories - 
@api_view(["GET"])
@permission_classes([AllowAny]) 
def user_booking_history(request):
    user_id = request.data.get('user_id')
    
    if not user_id:
        return Response({"error": "User ID is required"}, status=400)

    bookings = BookingHistory.objects.filter(user_id=user_id)

    if not bookings:
        return Response({"message": "No booking history found"}, status=404)

    serializer = BookinghistorySerializer(bookings, many=True) 
    return Response({"history":serializer.data})



# For the User Review on the perticular services or perticular provideer - 
@api_view(["POST"])
@permission_classes([AllowAny])
def submit_review(request):
    user_name = request.data.get("user_name")
    user_id = request.data.get("user_id")
    provider_name = request.data.get("provider_name")
    provider_id = request.data.get("provider_id")
    service_type = request.data.get("service_type")
    service_name = request.data.get("service_name")
    service_id = request.data.get("service_id")
    rating = request.data.get("rating")
    review = request.data.get("review")

    if not user_name or not provider_id or not provider_name or not service_type or not service_name or not service_id or not rating:
        return Response({"error": "User Name, Service Provider, and Rating are required"}, status=400)

    if not (1 <= int(rating) <= 5):
        return Response({"error": "Rating must be between 1 and 5"}, status=400)

    ServiceReview.objects.create(
        user_name=user_name,
        user_id=user_id,
        provider_name=provider_name,
        provider_id=provider_id,
        service_type=service_type,
        service_name=service_name,
        service_id=service_id,
        rating=rating,
        review=review
    )

    return Response({"message": "Review submitted successfully"}, status=201)



# For the get the user Reviews on a perticular services or Provider -
@api_view(["GET"])
@permission_classes([AllowAny])
def view_reviews(request):
    service_id = request.data.get("service_id") 

    if not service_id:
        return Response({"error": "Service Provider is required"}, status=400)

    reviews = ServiceReview.objects.filter(service_id=service_id)
    
    if not reviews:
        return Response({"message": "No reviews found for this provider"}, status=404)
    
    serializer = ServicereviewSerializer(reviews, many=True) 

    return Response({"reviews": serializer.data})

