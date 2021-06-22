from django.db import models
from django.core.files.storage import FileSystemStorage
from django.core.files import File


class Queries(models.Model):
    attach = models.FileField(storage=FileSystemStorage(location='collection'))
# Create your models here.
