from django.urls import path
from . import views
from .views import select_difficulty3, drag_drop_game, score3, sign_up, login_user, dashboard, select_difficulty3, drag_drop_game, store_drag_drop_score, score3, speed_challenge_intro  # ✅ Import views

urlpatterns = [

    path("login/", login_user, name="login"),
    path("sign-up/", sign_up, name="sign_up"),
    path("dashboard/", dashboard, name="dashboard"),  
    path('', views.home, name='home'),  # Set the home page
    path('speed-challenge/', views.speed_challenge, name='speed_challenge'),
    path('speed-challenge-feed/', views.speed_challenge_feed, name='speed_challenge_feed'),
    path("select-difficulty/", views.select_difficulty, name="select_difficulty"),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('numbers-games/', views.numbers_games, name='numbers_games'),  # Games under Numbers
    path('speed-challenge/', views.speed_challenge, name='speed_challenge'),  # Active Game


    path("select-difficulty2/", views.select_difficulty2, name="select_difficulty2"),
    path("sign-game2/", views.sign_game2, name="sign_game2"),

    path("store-drag-drop-score/", store_drag_drop_score, name="store_drag_drop_score"),


    path("select-difficulty3/", select_difficulty3, name="select_difficulty3"),
    path("drag-drop-game/", drag_drop_game, name="drag_drop_game"),
    path("score3/", score3, name="score3"),

    path("speed-challenge-intro/", speed_challenge_intro, name="speed_challenge_intro"),

]
