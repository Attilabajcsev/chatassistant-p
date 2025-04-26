# backend/chat/serializers.py
from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Conversation, Message, Document, BackgroundImage, Prompt, Settings


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "date_joined", "last_login"]
        extra_kwargs = {
            "password": {"write_only": True},
            "date_joined": {"read_only": True},
            "last_login": {"read_only": True}
        }

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = [
            "id", "title", "content", "source", "created_at", 
            "is_active", "user"
        ]
        read_only_fields = ["id", "created_at"]
        extra_kwargs = {
            "embedding": {"write_only": True},
            "user": {"read_only": True}
        }


class BackgroundImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = BackgroundImage
        fields = [
            "id", "name", "image", "image_url", "is_active", 
            "created_at", "user"
        ]
        read_only_fields = ["id", "created_at", "image_url"]
        extra_kwargs = {
            "image": {"write_only": True},
            "user": {"read_only": True}
        }
    
    def get_image_url(self, obj):
        if obj.image and hasattr(obj.image, 'url'):
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = [
            "id", "conversation", "role", "content", 
            "timestamp", "reference_documents"
        ]
        read_only_fields = ["id", "timestamp"]


class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Conversation
        fields = [
            "id", "session_id", "created_at", "updated_at", 
            "user", "messages"
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
        extra_kwargs = {
            "user": {"read_only": True}
        }


class PromptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prompt
        fields = [
            "id", "name", "assistant_role", "website_context",
            "knowledge_context", "response_guidelines", "restrictions",
            "is_active", "created_at", "updated_at", "user"
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
        extra_kwargs = {
            "user": {"read_only": True}
        }


class SettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Settings
        fields = [
            "id", "chatName", "colorPrimary", "buttonBg",
            "welcomeMessage", "disclaimerTitle", "disclaimerIntro",
            "disclaimerPoints", "acceptButtonText", "sendButtonText",
            "footerDisclaimer", "privacyPolicyText", "is_active",
            "created_at", "updated_at", "user"
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
        extra_kwargs = {
            "user": {"read_only": True}
        }