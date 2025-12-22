from rest_framework import serializers
from .models import Trade


class TradeSearchSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source='book.title', read_only=True)
    seller = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Trade
        fields = [
            'id',
            'title',
            'content',
            'sale_type',
            'price',
            'region',
            'status',
            'book_title',
            'seller',
            'image',
            'created_at',
        ]