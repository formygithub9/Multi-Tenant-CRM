from rest_framework import serializers

class LoginSerializer(serializers.Serializer):
    company_mobile = serializers.CharField(max_length=20)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class SignupSerializer(serializers.Serializer):
    company_name = serializers.CharField(max_length=255)
    company_mobile = serializers.CharField(max_length=20)
    company_email = serializers.EmailField()

    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)