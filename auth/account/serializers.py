from rest_framework import serializers
from .models import *


class SignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('email', 'password','name')

        extra_kwargs = {
            'email' : {'required':True ,'allow_blank':False},
            'password' : {'required':True ,'allow_blank':False,'min_length':8},
            'name':{'required':True ,'allow_blank':False}
        }

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('email','name') 


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)   