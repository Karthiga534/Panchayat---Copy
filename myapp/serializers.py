# from rest_framework import serializers
# from .models import CustomUser
# from django.contrib.auth.password_validation import validate_password

# class RegisterSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
#     confirm_password = serializers.CharField(write_only=True, required=True)

#     class Meta:
#         model = CustomUser
#         fields = "__all__"
#         # fields = ['username', 'phone_number', 'password', 'confirm_password', 'address', 'details']

#     def validate(self, attrs):
#         if attrs['password'] != attrs['confirm_password']:
#             raise serializers.ValidationError({"password": "Passwords do not match."})
#         return attrs

#     def create(self, validated_data):
#         validated_data.pop('confirm_password')  # remove confirm_password before saving
#         user = CustomUser.objects.create_user(**validated_data)
#         return user
