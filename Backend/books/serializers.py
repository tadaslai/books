from django.db import IntegrityError
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from Backend.books.models import FullUser, Author, Book, Review


class UserSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    password = serializers.CharField(write_only=True)
    username = serializers.CharField(max_length=150)
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    gender = serializers.ChoiceField(choices=['Male', 'Female', 'Other'])

    class Meta:
        model = FullUser
        fields = ('id', 'username', 'password', 'first_name', 'last_name', 'email', 'gender')

    def create(self, validated_data):
        try:
            user = FullUser.objects.create(
                username=validated_data['username'],
                first_name=validated_data['first_name'],
                last_name=validated_data['last_name'],
                email=validated_data['email'],
                gender=validated_data['gender'],
            )
        except IntegrityError:
            raise serializers.ValidationError('A user with this username already exists.')
        user.set_password(validated_data['password'])
        return user


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = '__all__'


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'
    def get_author_name(self, obj):
        return obj.author.name

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'

    def get_book_title(self, obj):
        return obj.book.title