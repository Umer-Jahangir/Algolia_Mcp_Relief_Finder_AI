from django.db import models

class Relief_Shelter(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()

    distance = models.FloatField(null=True, blank=True, help_text="Distance in miles from user or central point")
    is_open = models.BooleanField(default=True)
    is_24_7 = models.BooleanField(default=False)

    total_spaces = models.PositiveIntegerField(default=0)
    available_spaces = models.PositiveIntegerField(default=0)

    has_bed = models.BooleanField(default=False)
    has_food = models.BooleanField(default=False)
    has_water = models.BooleanField(default=False)
    has_medical = models.BooleanField(default=False)
    has_laundry = models.BooleanField(default=False)
    has_shower = models.BooleanField(default=False)
    has_case_management = models.BooleanField(default=False)
    has_mental_health = models.BooleanField(default=False)
    has_substance_abuse = models.BooleanField(default=False)

    accepts_families = models.BooleanField(default=False)
    accepts_men = models.BooleanField(default=False)
    accepts_women = models.BooleanField(default=False)
    accepts_pets = models.BooleanField(default=False)

    wheelchair_accessible = models.BooleanField(default=False)
    is_emergency = models.BooleanField(default=False)

    phone_number = models.CharField(max_length=20, blank=True)
    email = models.EmailField(null=True, blank=True)
    website = models.URLField(null=True, blank=True)

    hours_open = models.TimeField(null=True, blank=True)
    hours_close = models.TimeField(null=True, blank=True)

    source = models.CharField(max_length=100, default="Unknown")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
