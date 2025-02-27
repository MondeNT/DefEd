from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Player Profile Model
class PlayerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=50, unique=True)
    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    age = models.PositiveIntegerField()

    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
        ('Prefer not to say', 'Prefer not to say')
    ]
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES)
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    # ✅ Ensure these fields exist
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    school = models.CharField(max_length=150, blank=True, null=True)
    grade = models.CharField(max_length=20, blank=True, null=True)

    date_joined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} ({self.full_name})"

# Game Model
class Game(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()

    DIFFICULTY_CHOICES = [
        ('Easy', 'Easy'),
        ('Medium', 'Medium'),
        ('Hard', 'Hard')
    ]
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} - {self.difficulty}"


# Player Score Model
class PlayerScore(models.Model):
    player = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE, related_name="scores")
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="scores")
    score = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.player.username} - {self.game.title} - {self.score}"

    class Meta:
        ordering = ['-score']  # Order by highest score


# Leaderboard Model
class Leaderboard(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="leaderboard")
    player = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE, related_name="leaderboard_entries")
    highest_score = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.game.title} Leaderboard - {self.player.username} ({self.highest_score})"

    class Meta:
        ordering = ['-highest_score']  # Highest scores first


