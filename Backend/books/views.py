import json
import requests

import pytz
from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from Backend.books.models import FullUser, Author, Book, Review
from Backend.books.serializers import UserSerializer, AuthorSerializer, BookSerializer, ReviewSerializer
from rest_framework.views import APIView

class UserDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


@csrf_exempt
def login(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            token = user.auth_token.key
            response_data = {
                'token': token,
                'userId': user.id,
                'user': {
                    'username': user.username,
                    'email': user.email,
                }
            }
            return JsonResponse(response_data)
        else:
            return JsonResponse({'error': 'Invalid username or password'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)


class UserRegistrationView(generics.CreateAPIView):
    queryset = FullUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

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
        # Create a new author
        serializer = AuthorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    def put(self, request, author_id):
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
        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    def put(self, request, book_id, author_id=None):
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