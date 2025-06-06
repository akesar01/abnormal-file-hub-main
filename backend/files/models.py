from django.db import models
import uuid
import os
import hashlib

def file_upload_path(instance, filename):
    """Generate file path for new file upload"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('uploads', filename)

class FileContent(models.Model):
    """
    Stores unique file content for deduplication.
    Multiple File entries can reference the same FileContent.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content_hash = models.CharField(max_length=64, unique=True, db_index=True)
    file = models.FileField(upload_to=file_upload_path)
    size = models.BigIntegerField()
    reference_count = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'file_contents'
        indexes = [
            models.Index(fields=['content_hash']),
        ]

    def __str__(self):
        return f"FileContent({self.content_hash[:8]}...)"
class File(models.Model):
    """
    File metadata entry. References FileContent for actual file data.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content = models.ForeignKey(
        FileContent, 
        on_delete=models.PROTECT,  # Prevent accidental content deletion
        related_name='file_references'
    )
    original_filename = models.CharField(max_length=255, db_index=True)
    file_type = models.CharField(max_length=100, db_index=True)
    size = models.BigIntegerField(db_index=True)
    uploaded_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'files'
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['original_filename']),
            models.Index(fields=['file_type']),
            models.Index(fields=['size']),
            models.Index(fields=['uploaded_at']),
            models.Index(fields=['file_type', 'size']),  # Composite index for common filters
        ]
    
    def __str__(self):
        return self.original_filename

    @property
    def file(self):
        """Access the actual file through content relationship"""
        return self.content.file
