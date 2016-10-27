from django.db import models

# Create your models here.
class AndroidAppVersion(models.Model):
    version_code = models.PositiveIntegerField()
    version_name = models.CharField(max_length=50)
    package_name = models.CharField(max_length=50)
    release_date = models.CharField(max_length=20)
    release_notes = models.CharField(max_length=500)
    updated_time = models.DateTimeField(auto_now=True)

class AppPages(models.Model):
    cover_page = models.CharField(max_length=200)
    index_page = models.CharField(max_length=200)
    startup_page = models.CharField(max_length=200)

class CoverPages(models.Model):
    index = models.IntegerField()
    file_name = models.CharField(max_length=200)

class IndexPages(models.Model):
    index = models.IntegerField()
    file_name = models.CharField(max_length=200)

class StartupPages(models.Model):
    index = models.IntegerField()
    file_name = models.CharField(max_length=200)


