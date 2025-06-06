from django.core.management.base import BaseCommand
from files.models import FileContent

class Command(BaseCommand):
    help = 'Clean up orphaned file content with zero references'

    def handle(self, *args, **options):
        orphaned = FileContent.objects.filter(reference_count=0)
        count = orphaned.count()
        
        for content in orphaned:
            if content.file:
                content.file.delete(save=False)
            content.delete()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully cleaned up {count} orphaned file(s)'
            )
        )