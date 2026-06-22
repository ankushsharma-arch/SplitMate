from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Group


class UserSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model  = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name',
                  'is_staff', 'is_active', 'date_joined', 'last_login']


class GroupSerializer(serializers.ModelSerializer):
    members_detail = UserSummarySerializer(source='members', many=True, read_only=True)

    class Meta:
        model  = Group
        fields = '__all__'

    def create(self, validated_data):
        members = validated_data.pop('members', [])
        group   = Group.objects.create(**validated_data)
        group.members.add(group.created_by)
        if members:
            group.members.add(*members)
        return group


class GroupListSerializer(serializers.ModelSerializer):
    member_count = serializers.SerializerMethodField()

    class Meta:
        model  = Group
        fields = '__all__'

    def get_member_count(self, obj):
        return obj.members.count()
