from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth.hashers import make_password
from .serializers import *
from .models import *
from django.contrib.auth import authenticate,login
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
# Create your views here.

@api_view(['POST'])
def login_view(request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(email=serializer.validated_data['email'], password=serializer.validated_data['password'])
            if user is not None:
                login(request, user)
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                })
            return Response({'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
def register(request):
    data = request.data
    user = SignUpSerializer(data = data)
    
    if user.is_valid():
        if not CustomUser.objects.filter(email=data['email']).exists() :
            user = CustomUser.objects.create(
                email = data['email'] , 
                name = data['name'] , 
                password = make_password(data['password']),
            )
            return Response(
                {'message':'Your account registered susccessfully!' },
                    status=status.HTTP_201_CREATED
                    )
        else:
            return Response(
                {'eroor':'This email already exists!' },
                    status=status.HTTP_400_BAD_REQUEST
                    )
    else:
        return Response(user.errors)
    


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    user = UserSerializer(request.user, many=False)
    return Response(user.data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])

def update_user(request):
    user = request.user
    data = request.data
    user.name = data['name']
    user.email = data['email']
    if data['password'] != "":
        user.password =  make_password(data['password'])
  
    user.save()
    serializer = UserSerializer(user,many=False)
    return Response(serializer.data)
    



def get_current_host(request):
    protocol = request.is_secure() and 'https' or 'http'
    host = request.get_host()
    return "{protocol}://{host}/".format(protocol=protocol, host=host)


@api_view(['POST'])
def forgot_password(request):
    data = request.data
    user = get_object_or_404(CustomUser,email=data['email'])
    token = get_random_string(40)
    expire_date = datetime.now() + timedelta(minutes=30)
    user.profile.reset_password_token = token
    user.profile.reset_password_expire = expire_date
    user.profile.save()
    
    host = get_current_host(request)
    link = "http://localhost:8000/api/reset_password/{token}".format(token=token)
    body = "Your password reset link is : {link}".format(link=link)
    send_mail(
        "Paswword reset from eMarket",
        body,
        "eMarket@gmail.com",
        [data['email']]
    )
    return Response({'message': 'Password reset sent to {email}'.format(email=data['email'])})

 


@api_view(['POST'])
def reset_password(request,token):
    data = request.data
    user = get_object_or_404(CustomUser,profile__reset_password_token = token)

    if user.profile.reset_password_expire.replace(tzinfo=None) < datetime.now():
        return Response({'error': 'Token is expired'},status=status.HTTP_400_BAD_REQUEST)
    
    if data['password'] != data['confirmPassword']:
        return Response({'error': 'Password are not same'},status=status.HTTP_400_BAD_REQUEST)
    
    user.password = make_password(data['password'])
    user.profile.reset_password_token = ""
    user.profile.reset_password_expire = None 
    user.profile.save() 
    user.save()
    return Response({'message': 'Password reset done '})







