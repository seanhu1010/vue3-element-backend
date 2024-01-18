# user_info/serializers.py

# Importing the User model from Django's built-in authentication system
from django.contrib.auth.models import User

# Serializers define how to convert complex data types, such as Django models, into native Python datatypes that can be rendered into JSON.
from rest_framework import serializers

from .models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(use_url=True)

    class Meta:
        model = UserProfile
        fields = ("avatar", "gender", "occupation")


class UserSerializer(serializers.ModelSerializer):
    # date_joined字段将自动映射到User模型中的同名字段，并且只会显示年月日格式的日期
    date_joined = serializers.DateTimeField(format='%Y-%m-%d', read_only=True)
    avatar = serializers.ImageField(source='userprofile.avatar')
    # 修改成ChoiceField，以在页面上能进行选择
    # gender = serializers.ChoiceField(source='userprofile.gender', choices=(('男', '男'), ('女', '女'), ('未知', '未知')))
    gender = serializers.CharField(source='userprofile.gender')
    occupation = serializers.CharField(source='userprofile.occupation')

    class Meta:
        model = User
        fields = ("username", "password", "date_joined", "avatar", "gender", "occupation")
        extra_kwargs = {
            'password': {'write_only': True},
            'date_joined': {'read_only': True},
        }

    def create(self, validated_data):
        profile_data = validated_data.pop("userprofile", {})
        user = User.objects.create_user(**validated_data)
        if profile_data:
            UserProfile.objects.create(user=user, **profile_data)
        return user

    def update(self, instance, validated_data):
        profile_data = validated_data.pop("userprofile", {})
        user = super().update(instance, validated_data)
        for key, value in profile_data.items():
            setattr(instance.userprofile, key, value)
        instance.userprofile.save()
        return user
