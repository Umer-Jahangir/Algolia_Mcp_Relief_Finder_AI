from django.db import models
from django.utils import timezone

class disaster_alerts(models.Model):  
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=255, default="Unknown")
    disaster_type = models.CharField(max_length=100, default="Unknown")
    population_affected = models.IntegerField(default=0)
    disaster_time = models.DateTimeField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)   
    longitude = models.FloatField(null=True, blank=True)  
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'disaster_alerts'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.location}"

    def is_indexable(self):
        """Determine if this object should be indexed in Algolia"""
        return bool(self.title and self.location)

    def to_dict(self):
        """Custom serialization method for Algolia or API use"""
        return {
            'objectID': self.pk,
            'id': self.pk,
            'title': self.title,
            'description': self.description,
            'location': self.location,
            'disaster_type': self.disaster_type,
            'population_affected': self.population_affected,
            'disaster_time': self.disaster_time.isoformat() if self.disaster_time else None,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }

    def algolia_index_data(self):
        """Data to be indexed in Algolia"""
        return self.to_dict()
