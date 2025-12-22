from rest_framework import serializers
from .models import Book

class BookSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = [
            "id",
            "title",
            "author",
            "category",
            "adult",
        ]