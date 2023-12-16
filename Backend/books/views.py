import json
import requests

import pytz
from django.contrib.auth import authenticate
from django.http import JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, status, permissions
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from Backend.books.models import FullUser, Author, Book, Review
from Backend.books.serializers import UserSerializer, AuthorSerializer, BookSerializer, ReviewSerializer
from rest_framework.views import APIView


class IsStaffPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_staff

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True


class UserDetailsView(APIView):
    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LoginView(TokenObtainPairView):
    def post(self, request, **kwargs):
        user = request.user
        self.serializer = UserSerializer(user)
        super().post(self, request, **kwargs)


class UserRegistrationView(generics.CreateAPIView):
    queryset = FullUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AuthorView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, author_id=None):
        if author_id:
            try:
                author = Author.objects.get(pk=author_id)
                serializer = AuthorSerializer(author)
                return Response(serializer.data)
            except Author.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            authors = Author.objects.all()
            serializer = AuthorSerializer(authors, many=True)
            return Response(serializer.data)

    def post(self, request):
        self.permission_classes = [IsStaffPermission]
        if not request.user.is_staff:
            return Response(status=status.HTTP_403_FORBIDDEN)
        # Create a new author
        serializer = AuthorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    def put(self, request, author_id):
        self.permission_classes = [IsAuthenticated, IsStaffPermission]

        try:
            author = Author.objects.get(pk=author_id)
        except Author.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = AuthorSerializer(author, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    def delete(self, request, author_id):
        self.permission_classes = [IsAuthenticated, IsStaffPermission]

        try:
            author = Author.objects.get(pk=author_id)
        except Author.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        author.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BookView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, book_id=None, author_id=None):
        if book_id:
            try:
                book = Book.objects.get(pk=book_id)
                book_serializer = BookSerializer(book)
                review_queryset = Review.objects.filter(book=book)
                review_serializer = ReviewSerializer(review_queryset, many=True)

                serialized_book = book_serializer.data

                serialized_book['author_name'] = book.author.name
                serialized_book['reviews'] = review_serializer.data

                return Response(serialized_book)
            except Book.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            books = Book.objects.all()
            if author_id:
                try:
                    author = Author.objects.get(id=author_id)
                except:
                    return Response(status=status.HTTP_404_NOT_FOUND)
                books = books.filter(author_id=author_id)

            data = []
            for book in books:
                serializer = BookSerializer(book)
                book_data = serializer.data
                book_data['author_name'] = book.author.name
                data.append(book_data)

            return Response(data)

    def post(self, request, author_id=None):
        self.permission_classes = [IsAuthenticated, IsStaffPermission]
        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    def put(self, request, book_id, author_id=None):
        self.permission_classes = [IsAuthenticated, IsStaffPermission]

        try:
            book = Book.objects.get(pk=book_id)
        except Book.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = BookSerializer(book, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    def delete(self, request, book_id, author_id=None):
        self.permission_classes = [IsAuthenticated, IsStaffPermission]

        try:
            book = Book.objects.get(pk=book_id)
        except Book.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        book.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ReviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, review_id=None, author_id=None, book_id=None):
        if review_id and author_id and book_id:
            try:
                review = Review.objects.get(pk=review_id)
                serializer = ReviewSerializer(review)
                data = serializer.data
                data['book_title'] = review.book.title
                return Response(data)
            except Review.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            reviews = Review.objects.all()
            if author_id and book_id:
                try:
                    book = Book.objects.get(id=book_id)
                except:
                    return Response(status=status.HTTP_404_NOT_FOUND)
                reviews = reviews.filter(book_id=book.id)

            data = []
            for review in reviews:
                serializer = ReviewSerializer(review)
                review_data = serializer.data
                review_data['book_title'] = review.book.title
                review_data['creator'] = review.user.username

                data.append(review_data)
            return Response(data)

    def post(self, request, author_id=None, book_id=None):
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    def put(self, request, review_id, author_id=None, book_id=None):
        try:
            review = Review.objects.get(pk=review_id)
        except Review.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = ReviewSerializer(review, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    def delete(self, request, review_id, author_id=None, book_id=None):
        try:
            review = Review.objects.get(pk=review_id)
        except Review.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


def custom404(request, exception=None):
    return JsonResponse({
        'status_code': 404,
        'error': 'The resource was not found'
    })


class NotFoundView(APIView):
    def get(self, request):
        Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


@csrf_exempt
def method_not_allowed(request, *args, **kwargs):
    response_data = {
        'error': 'Method Not Allowed',
        'message': 'This method is not allowed for this endpoint.',
    }
    return JsonResponse(response_data, status=405)
