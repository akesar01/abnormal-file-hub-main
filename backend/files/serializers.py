from rest_framework import serializers
from .models import File, FileContent
from .utils import format_file_size

class FileContentSerializer(serializers.ModelSerializer):
    """Serializer for file content details"""
    class Meta:
        model = FileContent
        fields = ['id', 'content_hash', 'size', 'reference_count', 'created_at']
        read_only_fields = ['id', 'content_hash', 'reference_count', 'created_at']

class FileSerializer(serializers.ModelSerializer):
    """Main file serializer with deduplication info"""
    file_url = serializers.SerializerMethodField()
    is_duplicate = serializers.SerializerMethodField()
    storage_saved = serializers.SerializerMethodField()
    formatted_size = serializers.SerializerMethodField()

    class Meta:
        model = File
        fields = [
            'id', 'original_filename', 'file_type', 'size', 
            'formatted_size', 'uploaded_at', 'file_url',
            'is_duplicate', 'storage_saved'
        ]
        read_only_fields = ['id', 'uploaded_at', 'is_duplicate', 'storage_saved']

    def get_file_url(self, obj):
        request = self.context.get('request')
        if request and obj.file:
            return request.build_absolute_uri(obj.file.url)
        return obj.file.url if obj.file else None

    def get_is_duplicate(self, obj):
        """Check if this file was deduplicated"""
        return obj.content.reference_count > 1

    def get_storage_saved(self, obj):
        """Calculate storage saved if this is a duplicate"""
        if obj.content.reference_count > 1:
            return obj.size
        return 0

    def get_formatted_size(self, obj):
        """Return human-readable file size"""
        return format_file_size(obj.size)

class FileUploadSerializer(serializers.Serializer):
    """Serializer for file upload validation"""
    file = serializers.FileField(required=True)
    
    def validate_file(self, value):
        """Validate uploaded file"""
        # Check file size (10MB limit)
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("File size cannot exceed 10MB")
        return value 