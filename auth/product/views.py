from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes,parser_classes
from rest_framework.response import Response
from .filtters import ProductsFilter
from .serializers import *
from .models import *
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.storage import default_storage
from urllib.parse import urljoin

# Create your views here.

@api_view(['GET'])
def get_all_products(request):
    filterset=ProductsFilter(request.GET,queryset=Product.objects.all().order_by('id'))
    products=Product.objects.all()   
    serializer = ProductSerializer(filterset.qs,many=True)
    # Add the base URL to image links

    # Add the base URL to image links
    BASE_URL = request.build_absolute_uri('/')

    # Add the base URL to image links and include image IDs
    for product_data in serializer.data:
        images = product_data['images']
        image_data = []
        for image in images:
            image_url = urljoin(BASE_URL, image['image']) 
            image_with_id = {
                'id': image['id'],
                'image': image_url,
                'createAt': image['createAt'],
                'product': image['product']
            }
            image_data.append(image_with_id)
        product_data['images'] = image_data

    return Response({"product": serializer.data})



@api_view(['GET'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def get_by_id_product(request,pk):
    products = get_object_or_404(Product,id=pk)
    serializer = ProductSerializer(products,many=False)
 

    BASE_URL = request.build_absolute_uri('/')  # Include the trailing slash
        
    # Add the base URL to image links
    images = serializer.data['images']
    image_urls = [BASE_URL + image['image'] for image in images]  # Remove the trailing slash
    serializer.data['images'] = image_urls

    return Response({"product":serializer.data})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def new_product(request):
        serializer = ProductSerializer(data=request.data)

        if serializer.is_valid():
            # Create the product instance with user data.
            product = Product.objects.create(user=request.user, **serializer.validated_data)

            # Handle the image upload.
            image_files = request.FILES.getlist('images')
            for image_file in image_files:
                product_image = ProductImage(product=product, image=image_file)
                product_image.save()

            notification_message = f'New product added: {product.name}'
            notification = Notification(user=request.user, message=notification_message)
            notification.save()
            # Retrieve the full product information including images.
            serializer = ProductSerializer(product)
            response_data = {
            'message': 'Product created successfully',
            'data': serializer.data,
            }
            return Response(response_data,status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_product(request,pk):
    product=get_object_or_404(Product,id=pk)
    if product.user != request.user:
        return Response({"error":"Sorry you can not delete this product"}
                        , status=status.HTTP_403_FORBIDDEN)
    # Delete the previous image files
    product_images = ProductImage.objects.filter(product=product)
    for product_image in product_images:
        # Delete image file from storage
        if product_image.image:
            default_storage.delete(product_image.image.path)

        # Delete the ProductImage record from the database
        product_image.delete()

    image_files = request.FILES.getlist('images')
    for image_file in image_files:
        product_image = ProductImage(product=product, image=image_file)
        product_image.save()

    serializer = ProductSerializer(product, data=request.data)

    if serializer.is_valid():
        serializer.save(user=request.user)
        response_data = {
            'message': 'Product updated successfully',
            'data': serializer.data,
            }
        return Response(response_data,status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_product(request,pk):
    product = get_object_or_404(Product,id=pk)
    if product.user != request.user:
        return Response({"error":"Sorry you can not delete this product"}
                        , status=status.HTTP_403_FORBIDDEN)
    # Delete the previous image files
    product_images = ProductImage.objects.filter(product=product)
    for product_image in product_images:
        # Delete image file from storage
        if product_image.image:
            default_storage.delete(product_image.image.path)

        # Delete the ProductImage record from the database
        product_image.delete()
    

    product.delete() 
    return Response({"message":"Delete action is done"},status=status.HTTP_200_OK)



@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def mark_notification_as_read(request, notification_id):
    try:
        notification = Notification.objects.get(id=notification_id)
        notification.is_read = True
        notification.save()
        return Response({'message': 'Notification marked as read'})
    except Notification.DoesNotExist:
        return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)