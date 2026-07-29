from rest_framework import serializers

class LoginSerializer(serializers.Serializer):
    company_mobile = serializers.CharField(max_length=20)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)