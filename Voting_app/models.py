from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Position(models.Model):
    title = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "Positions"
    def __str__(self):
        return self.title

class Department(models.Model):
    dept = models.CharField(max_length=100,blank=False, null=False)

    class Meta:
        verbose_name_plural = "Departments"
    def __str__(self):
        return self.dept

class Candidate(models.Model):
    name = models.CharField(max_length=100, unique=False)
    candidate_position = models.ForeignKey(Position, on_delete=models.CASCADE)
    votes = models.BigIntegerField(default=0, blank=True, null=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='candidate_images/', null=True, blank=True)

    class Meta:
        verbose_name_plural = "Candidates"
    def __str__(self) -> str:
        return f"{self.name } {self.candidate_position}"

class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'position')
        verbose_name_plural = "Votes"

    def __str__(self):
        return f"{self.user.username} voted for {self.candidate.name} as {self.position.title}"



class Election(models.Model):
    is_active = models.BooleanField(default=False)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.PositiveIntegerField(default=0)  # Admin sets this

    def time_left(self):
        from django.utils import timezone
        if self.is_active and self.end_time:
            delta = self.end_time - timezone.now()
            return max(int(delta.total_seconds()), 0)
        return 0

    class Meta:
        unique_together = ('start_time', 'end_time')
        verbose_name_plural = "Elections"

    def __str__(self):
        return f"{self.start_time} - {self.end_time} ({'Active' if self.is_active else 'Inactive'})"



