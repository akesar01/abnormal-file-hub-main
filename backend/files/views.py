from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import File
from .serializers import FileSerializer
from django.db.models import Q, Sum
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .models import FileContent
from .serializers import FileUploadSerializer
from .utils import calculate_file_hash
from django.db import models

# Create your views here.

class FileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for file operations with deduplication and search capabilities.
    """
    serializer_class = FileSerializer
    
    def get_queryset(self):
        """
        Get filtered queryset based on query parameters.
        Supports search and multiple filters.
        """
        queryset = File.objects.select_related('content').all()
        
        # Search by filename
        search = self.request.query_params.get('search', '')
        if search:
            queryset = queryset.filter(original_filename__icontains=search)
        
        # Filter by file type
        file_type = self.request.query_params.get('file_type', '')
        if file_type:
            queryset = queryset.filter(file_type__iexact=file_type)
        
        # Filter by size range
        min_size = self.request.query_params.get('min_size', '')
        if min_size.isdigit():
            queryset = queryset.filter(size__gte=int(min_size))
        
        max_size = self.request.query_params.get('max_size', '')
        if max_size.isdigit():
            queryset = queryset.filter(size__lte=int(max_size))
        
        # Filter by upload date range
        start_date = self.request.query_params.get('start_date', '')
        if start_date:
            queryset = queryset.filter(uploaded_at__date__gte=start_date)
        
        end_date = self.request.query_params.get('end_date', '')
        if end_date:
            queryset = queryset.filter(uploaded_at__date__lte=end_date)
        
        # Apply ordering
        ordering = self.request.query_params.get('ordering', '-uploaded_at')
        if ordering in ['uploaded_at', '-uploaded_at', 'size', '-size', 'original_filename', '-original_filename']:
            queryset = queryset.order_by(ordering)
        
        return queryset

    def create(self, request, *args, **kwargs):
        """
        Handle file upload with deduplication.
        """
        upload_serializer = FileUploadSerializer(data=request.data)
        upload_serializer.is_valid(raise_exception=True)
        
        file_obj = upload_serializer.validated_data['file']
        
        # Calculate file hash for deduplication
        content_hash = calculate_file_hash(file_obj)
        
        # Check if content already exists
        file_content, created = FileContent.objects.get_or_create(
            content_hash=content_hash,
            defaults={
                'file': file_obj,
                'size': file_obj.size
            }
        )
        
        # If content existed, increment reference count
        if not created:
            file_content.reference_count += 1
            file_content.save(update_fields=['reference_count'])
        
        # Create file metadata entry
        file_instance = File.objects.create(
            content=file_content,
            original_filename=file_obj.name,
            file_type=file_obj.content_type or 'application/octet-stream',
            size=file_obj.size
        )
        
        # Serialize response
        serializer = self.get_serializer(file_instance)
        response_data = serializer.data
        
        # Add upload metadata
        response_data['upload_details'] = {
            'was_deduplicated': not created,
            'content_hash': content_hash[:8] + '...',
            'storage_saved': file_obj.size if not created else 0
        }
        
        return Response(
            response_data,
            status=status.HTTP_201_CREATED
        )

    def destroy(self, request, *args, **kwargs):
        """
        Delete file and handle content cleanup.
        """
        instance = self.get_object()
        file_content = instance.content
        
        # Delete the file metadata
        instance.delete()
        
        # Decrement reference count
        file_content.reference_count -= 1
        
        # If no more references, delete the content
        if file_content.reference_count <= 0:
            # Delete the actual file
            if file_content.file:
                file_content.file.delete(save=False)
            file_content.delete()
        else:
            file_content.save(update_fields=['reference_count'])
        
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get storage statistics and deduplication metrics.
        """
        total_files = File.objects.count()
        unique_contents = FileContent.objects.count()
        
        # Calculate total storage used
        total_storage = FileContent.objects.aggregate(
            total=Sum('size')
        )['total'] or 0
        
        # Calculate potential storage without deduplication
        potential_storage = File.objects.aggregate(
            total=Sum('size')
        )['total'] or 0
        
        # Storage saved through deduplication
        storage_saved = potential_storage - total_storage
        
        # Get file type distribution
        file_types = File.objects.values('file_type').annotate(
            count=models.Count('id'),
            total_size=Sum('size')
        ).order_by('-count')[:10]
        
        return Response({
            'summary': {
                'total_files': total_files,
                'unique_files': unique_contents,
                'deduplication_ratio': f"{(1 - unique_contents/total_files)*100:.1f}%" if total_files > 0 else "0%",
                'total_storage_used': total_storage,
                'storage_saved': storage_saved,
                'storage_efficiency': f"{(storage_saved/potential_storage)*100:.1f}%" if potential_storage > 0 else "0%"
            },
            'file_types': list(file_types)
        })

    @action(detail=False, methods=['get'])
    def duplicates(self, request):
        """
        List files that share the same content.
        """
        # Get content with multiple references
        duplicate_contents = FileContent.objects.filter(
            reference_count__gt=1
        ).order_by('-reference_count')
        
        duplicates_data = []
        for content in duplicate_contents:
            files = File.objects.filter(content=content).values(
                'id', 'original_filename', 'uploaded_at'
            )
            duplicates_data.append({
                'content_hash': content.content_hash[:8] + '...',
                'size': content.size,
                'reference_count': content.reference_count,
                'storage_saved': content.size * (content.reference_count - 1),
                'files': list(files)
            })
        
        return Response({
            'total_duplicate_groups': len(duplicates_data),
            'duplicates': duplicates_data
        })
