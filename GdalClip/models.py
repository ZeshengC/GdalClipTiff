from __future__ import unicode_literals

from django.db import models

# Create your models here.

class ClipRequest(models.Model):
    userId  = models.IntegerField()
    inputShpPath = models.TextField()
    outputTiffPath = models.TextField()
    inputTiffPath = models.TextField()
    
