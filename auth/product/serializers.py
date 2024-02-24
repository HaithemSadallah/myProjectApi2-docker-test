from rest_framework import serializers
from .models import *

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = "__all__"

class ProductSerializer(serializers.ModelSerializer):
 
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ('id','name', 'description', 'price', 'user', 'images')

    def create(self, validated_data):
        images_data = validated_data.pop('images', [])
        product = Product.objects.create(**validated_data)
        for image_data in images_data:
            ProductImage.objects.create(product=product, **image_data)
        return product