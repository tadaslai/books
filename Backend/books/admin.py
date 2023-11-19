from django.contrib import admin

from Backend.books.models import FullUser, Book, Review, Author


# Register your models here.

class FullUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'password', 'first_name', 'last_name', 'email', 'gender',
                    'is_staff', 'auth_token')

class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name', "bio")
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'publication_date', 'isbn')

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('book', 'user', 'rating', 'review_text', "created_at")

admin.site.register(FullUser, FullUserAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Book, BookAdmin)
admin.site.register(Review, ReviewAdmin)
