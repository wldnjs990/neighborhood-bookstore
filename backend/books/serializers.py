from rest_framework import serializers
from .models import Book

class BookSearchSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Book
        fields = [
            'id',
            'title',
            'author',
            'publisher',
            'cover',
            'average_rating',
            'rating_count',
            'category',
        ]
        read_only_fields = ['id']