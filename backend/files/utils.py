import hashlib

def calculate_file_hash(file_obj):
    """
    Calculate SHA-256 hash of file content.
    Reads file in chunks to handle large files efficiently.
    """
    hasher = hashlib.sha256()
    
    # Reset file pointer to beginning
    file_obj.seek(0)
    
    # Read file in 64KB chunks
    for chunk in iter(lambda: file_obj.read(65536), b''):
        hasher.update(chunk)
    
    # Reset file pointer for subsequent operations
    file_obj.seek(0)
    
    return hasher.hexdigest()

def format_file_size(bytes_size):
    """Convert bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} PB"
