from rest_framework import serializers
from webserviceApp.models import ProviderService
from . models import BookingHistory, ServiceReview, User
from bson import ObjectId, Decimal128


#-------------------------------- For Providers --------------------------------#

# Provider Data Serializers -
class ProviderServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model=ProviderService
        fields = '__all__'


    def validate_provider(self, value):
    # Ensure provider is a string
        if not isinstance(value, str):
            raise serializers.ValidationError("Provider ID must be a string.")
        return value
    




#------------------------------- For Clients --------------------------------#


# For the Users Data Serializers(Included=> Admin, Provider and Clients)
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'password', 'first_name', 'last_name']

    
    def create(self, validated_data):
        # Hash the password before saving
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)
        return user
    

class BookinghistorySerializer(serializers.ModelSerializer):
    class Meta:
        model=BookingHistory
        fields='__all__'

        
# For the Services Reviw System -
class ServicereviewSerializer(serializers.ModelSerializer):
    class Meta:
        model=ServiceReview
        fields='__all__'
