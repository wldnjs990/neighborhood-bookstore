from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'password_confirm', 'email', 'nickname', 'age')
        extra_kwargs = {
            'email': {'required': False},
            'nickname': {'required': False},
            'age': {'required': False},
        }

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("비밀번호가 일치하지 않습니다.")
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            nickname=validated_data.get('nickname'),
            age=validated_data.get('age')
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'nickname', 'age', 'book_mbti')
        read_only_fields = ('id',)


class ProfileUpdateSerializer(serializers.ModelSerializer):
    """프로필 수정용 Serializer"""
    class Meta:
        model = User
        fields = ('email', 'nickname', 'age', 'book_mbti')
        extra_kwargs = {
            'email': {'required': False},
            'nickname': {'required': False},
            'age': {'required': False},
            'book_mbti': {'required': False},
        }

    def validate_nickname(self, value):
        """nickname 중복 검증 (본인 제외)"""
        user = self.context['request'].user
        if value and User.objects.exclude(pk=user.pk).filter(nickname=value).exists():
            raise serializers.ValidationError("이미 사용 중인 닉네임입니다.")
        return value
