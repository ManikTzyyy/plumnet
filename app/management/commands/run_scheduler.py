from django.core.management.base import BaseCommand
from app import jobs   # ganti scheduler -> jobs

class Command(BaseCommand):
    help = "Run APScheduler jobs"

    def handle(self, *args, **options):
        jobs.start()  # panggil fungsi start() dari jobs.py
        self.stdout.write(self.style.SUCCESS("Scheduler started"))
        import time
        while True:
            time.sleep(1)

