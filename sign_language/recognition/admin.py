from django.contrib import admin
from .models import PlayerProfile, Game, PlayerScore, Leaderboard

# Register your models here.
@admin.register(PlayerProfile)
class PlayerProfileAdmin(admin.ModelAdmin):
    list_display = ('username', 'full_name', 'email', 'age', 'gender', 'date_joined')
    search_fields = ('username', 'full_name', 'email')
    list_filter = ('gender', 'date_joined')
    ordering = ('-date_joined',)

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('title', 'difficulty', 'is_active')
    search_fields = ('title',)
    list_filter = ('difficulty', 'is_active')
    ordering = ('title',)

@admin.register(PlayerScore)
class PlayerScoreAdmin(admin.ModelAdmin):
    list_display = ('player', 'game', 'score', 'timestamp')
    search_fields = ('player__username', 'game__title')
    list_filter = ('game', 'timestamp')
    ordering = ('-score',)

@admin.register(Leaderboard)
class LeaderboardAdmin(admin.ModelAdmin):
    list_display = ('game', 'player', 'highest_score', 'last_updated')
    search_fields = ('player__username', 'game__title')
    list_filter = ('game',)
    ordering = ('-highest_score',)