from django.shortcuts import render
from django.http import StreamingHttpResponse
import cv2
import mediapipe as mp
import os
import random
import time
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect






from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
from django.contrib import messages

# Get the user model dynamically (for custom user models)
User = get_user_model()

def login_user(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user = User.objects.get(email=email)  # Find user by email
        except User.DoesNotExist:
            user = None

        if user:
            user = authenticate(request, username=user.username, password=password)  # Authenticate using username

        if user is not None:
            login(request, user)
            return redirect("dashboard")  # Redirect to dashboard
        else:
            messages.error(request, "❌ Invalid email or password. Please try again.")

    return render(request, "recognition/home.html")


from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login
from .models import PlayerProfile

def sign_up(request):
    if request.method == "POST":
        username = request.POST["username"]
        full_name = request.POST["full_name"]
        email = request.POST["email"]
        age = request.POST["age"]
        gender = request.POST["gender"]
        phone_number = request.POST["phone_number"]
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]

        # Check if passwords match
        if password != confirm_password:
            return render(request, "recognition/sign_up.html", {"error": "Passwords do not match."})

        # Check if username is already taken
        if User.objects.filter(username=username).exists():
            return render(request, "recognition/sign_up.html", {"error": "Username already exists."})

        # Check if email is already registered
        if User.objects.filter(email=email).exists():
            return render(request, "recognition/sign_up.html", {"error": "Email is already registered."})

        # Create User in Django's built-in authentication system
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()

        # Create associated PlayerProfile
        player_profile = PlayerProfile.objects.create(
            user=user,
            username=username,
            full_name=full_name,
            email=email,
            age=age,
            gender=gender,
            phone_number=phone_number,
        )
        player_profile.save()

        # Log the user in and redirect to the dashboard or home
        login(request, user)
        return redirect("home")  # Redirect to home/dashboard after signup

    return render(request, "recognition/sign_up.html")


@login_required
def dashboard(request):
    """Dashboard page after login"""
    return render(request, "recognition/dashboard.html", {"user": request.user})



class handDetector:
    def __init__(self, mode=False, maxHands=1, detectionCon=0.75, trackCon=0.75):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.maxHands,
            min_detection_confidence=self.detectionCon,
            min_tracking_confidence=self.trackCon,
        )
        self.mpDraw = mp.solutions.drawing_utils
        self.results = None

    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)

        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)
        return img

    def findPosition(self, img, handNo=0, draw=True):
        lmList = []
        if self.results and self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(myHand.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 10, (255, 0, 0), cv2.FILLED)
        return lmList


import cv2
import random
import time


from django.shortcuts import render, redirect
from django.http import StreamingHttpResponse, JsonResponse
import cv2
import mediapipe as mp
import os
import random
import time
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Max

from .models import PlayerScore, PlayerProfile, Game, Leaderboard  # Import necessary models

# Hand detection class (unchanged)
class handDetector:
    def __init__(self, mode=False, maxHands=1, detectionCon=0.75, trackCon=0.75):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.maxHands,
            min_detection_confidence=self.detectionCon,
            min_tracking_confidence=self.trackCon,
        )
        self.mpDraw = mp.solutions.drawing_utils
        self.results = None

    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)

        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)
        return img

    def findPosition(self, img, handNo=0, draw=True):
        lmList = []
        if self.results and self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(myHand.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 10, (255, 0, 0), cv2.FILLED)
        return lmList


from django.shortcuts import render, redirect
from django.http import StreamingHttpResponse, JsonResponse
import random
import time
import cv2
import mediapipe as mp
from django.contrib.auth.decorators import login_required
from django.db.models import Max
from .models import PlayerScore, PlayerProfile, Game, Leaderboard  # Import models


# ✅ Ensure difficulty selection before game starts
@login_required
def select_difficulty(request):
    """Renders the difficulty selection page before starting the game."""
    if request.method == "POST":
        difficulty = request.POST.get("difficulty")
        if difficulty in ["easy", "medium", "hard"]:
            request.session["difficulty"] = difficulty  # ✅ Save difficulty in session
            return redirect("speed_challenge")
    return render(request, "recognition/select_difficulty.html")


# ✅ Define Hand Detector Class (No Changes Here)
class handDetector:
    def __init__(self, detectionCon=0.75):
        self.detectionCon = detectionCon
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(min_detection_confidence=self.detectionCon)
        self.mpDraw = mp.solutions.drawing_utils
        self.results = None

    def findHands(self, img):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)
        return img

    def findPosition(self, img):
        lmList = []
        if self.results and self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[0]
            for id, lm in enumerate(myHand.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([id, cx, cy])
        return lmList


# ✅ Game Logic: Restored to Full Functionality
@login_required
def generate_speed_challenge_frames(request, level, user):
    """Game logic for speed challenge with real-time number detection and score tracking."""

    cap = cv2.VideoCapture(0)
    detector = handDetector(detectionCon=0.75)

    # ✅ Ensure the player profile exists
    try:
        player = PlayerProfile.objects.get(user=user)
    except PlayerProfile.DoesNotExist:
        print("❌ Player profile not found for user:", user)
        return  

    # Define finger configurations for numbers 0-9
    fingerConfigurations = {
        (0, 0, 0, 0, 0): 0,
        (0, 1, 0, 0, 0): 1,
        (0, 1, 1, 0, 0): 2,
        (0, 0, 1, 1, 1): 3,
        (0, 1, 1, 1, 1): 4,
        (1, 1, 1, 1, 1): 5,
        (1, 0, 0, 0, 0): 6,
        (1, 1, 0, 0, 0): 7,
        (1, 1, 1, 0, 0): 8,
        (1, 1, 1, 1, 0): 9,
    }

    # ✅ Restore Difficulty Selection and Game Duration
    difficulty_map = {"easy": 90, "medium": 60, "hard": 45}
    number_range = range(0, 10) if level == "hard" else range(0, 6)
    total_time = difficulty_map.get(level, 60)

    current_number = random.choice(number_range)
    start_time = time.time()
    score = 0
    correct_answer_registered = False  # ✅ Ensure score only increases once per correct answer

    while True:
        success, img = cap.read()
        if not success:
            break

        img = detector.findHands(img)
        lmList = detector.findPosition(img)

        detected_number = None
        if len(lmList) != 0:
            fingers = [1 if lmList[4][1] > lmList[3][1] else 0]  # Thumb logic
            fingers += [1 if lmList[4 + id * 4][2] < lmList[4 + id * 4 - 2][2] else 0 for id in range(1, 5)]
            detected_number = fingerConfigurations.get(tuple(fingers), None)

            # ✅ Ensure score increases only once per correct answer
            if detected_number == current_number and not correct_answer_registered:
                score += 1
                current_number = random.choice(number_range)  # ✅ Change number after correct answer
                correct_answer_registered = True  # ✅ Prevent multiple increments for the same answer
            elif detected_number != current_number:
                correct_answer_registered = False  # Reset when incorrect input is detected

        elapsed_time = time.time() - start_time
        time_left = max(0, total_time - elapsed_time)

        cv2.putText(img, f"Number: {current_number}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(img, f"Score: {score}", (300, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(img, f"Time: {int(time_left)}s", (500, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        if time_left <= 0:
            break

        ret, buffer = cv2.imencode(".jpg", img)
        frame = buffer.tobytes()
        yield b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"

    cap.release()

    # ✅ Ensure the game exists
    game, created = Game.objects.get_or_create(title="Speed Challenge", difficulty=level)

    # ✅ Store the score
    PlayerScore.objects.create(player=player, game=game, score=score)

    # ✅ Update leaderboard
    leaderboard_entry, created = Leaderboard.objects.get_or_create(game=game, player=player)
    if score > leaderboard_entry.highest_score:
        leaderboard_entry.highest_score = score
        leaderboard_entry.save()


# ✅ **Ensure game can only start if difficulty is selected**
@login_required
def speed_challenge(request):
    """Renders game page, but ensures difficulty is selected first."""
    if "difficulty" not in request.session:  # ✅ Prevent game from starting without difficulty
        return redirect("select_difficulty")

    level = request.session["difficulty"]
    return render(request, "recognition/speed_challenge.html", {"level": level})


# ✅ Ensure game correctly streams video
@login_required
def speed_challenge_feed(request):
    """✅ Fixed: Correctly Pass `request.user` into Function"""
    level = request.session.get("difficulty", "medium")  # ✅ Use saved difficulty
    return StreamingHttpResponse(
        generate_speed_challenge_frames(request, level, request.user),  # ✅ Fix: Pass request properly
        content_type="multipart/x-mixed-replace; boundary=frame"
    )


# ✅ API to Store Score
@login_required
def store_speed_challenge_score(request):
    """Stores speed challenge score after game ends."""
    if request.method == "POST":
        score = int(request.POST.get("score", 0))
        level = request.session.get("difficulty", "medium")

        game, created = Game.objects.get_or_create(title="Speed Challenge", difficulty=level)

        try:
            player = PlayerProfile.objects.get(user=request.user)
        except PlayerProfile.DoesNotExist:
            return JsonResponse({"error": "Player profile not found"}, status=400)

        PlayerScore.objects.create(player=player, game=game, score=score)

        leaderboard_entry, created = Leaderboard.objects.get_or_create(game=game, player=player)
        if score > leaderboard_entry.highest_score:
            leaderboard_entry.highest_score = score
            leaderboard_entry.save()

        return JsonResponse({"message": "Score saved successfully!", "score": score})

    return JsonResponse({"error": "Invalid request"}, status=400)



# ✅ **Difficulty Selection Before Game**
@login_required
def select_difficulty(request):
    """Forces user to select difficulty before playing."""
    if request.method == "POST":
        difficulty = request.POST.get("difficulty")
        if difficulty in ["easy", "medium", "hard"]:
            request.session["difficulty"] = difficulty  # ✅ Save difficulty in session
            return redirect("speed_challenge")  # ✅ Redirect to the game
    return render(request, "recognition/select_difficulty.html")





def home(request):
    return render(request, 'recognition/home.html')



def update_profile(request):
    if request.method == 'POST':
        # Handle form submission
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        phone_number = request.POST.get('phone_number')

        # Validate inputs
        if password != confirm_password:
            return render(request, "update_profile.html", {
                'error': "Passwords do not match",
                'form_data': request.POST
            })
        
        # Simulate saving updated data (replace this with database logic)
        return render(request, "dashboard.html", {'message': "Profile updated successfully!"})
    
    return render(request, "recognition/update_profile.html")


from django.shortcuts import render

def numbers_games(request):
    # Pass data about games to the template
    games = [
        {
            'title': 'Speed Challenge Game',
            'description': 'A fast-paced game to test your knowledge of signing numbers. Match the correct hand gesture before the timer runs out!',
            'url': '/speed-challenge-intro/',
            'image': 'https://img.freepik.com/free-photo/pleased-confident-middleaged-woman-wearing-tshirt-looking-camera-showing-promise-gesture-isolated-olive-green-background_141793-136105.jpg?t=st=1737749719~exp=1737753319~hmac=93fc1a4a9d102a7bb1fae8281438c586046aa606ed14443773677fc22201681d&w=996',
            'is_active': True
        },
        {
            'title': 'Number Matching Game',
            'description': 'Match the numbers with their respective signs in this fun and engaging game.',
            'url': '/select-difficulty2/',
            'image': 'https://img.freepik.com/free-vector/3d-colorful-bullet-point-collection_23-2148090452.jpg?t=st=1737986584~exp=1737990184~hmac=776265d0617dd8f51f7349ccaa3eea4a9db04ea28add37523ba223279e8b2617&w=740',
            'is_active': True
        },
        {
            'title': 'Drag and Drop Game',
            'description': 'Test your ability to recognize number signs in various contexts. Challenge yourself to match the correct number signs with their corresponding visual representations, improving your recognition skills and memory.',
            'url': '/select-difficulty3/',
            'image': 'https://img.freepik.com/free-photo/top-view-numbers-education-day_23-2149240994.jpg?t=st=1738249974~exp=1738253574~hmac=4aaf6f92b3a7871bb3cbbf7022ffe9d9008164bb6f626a51d2bf9676b83dd1f9&w=996',
            'is_active': False
        },
    ]
    return render(request, "recognition/numbers_games.html", {"games": games})






from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import random
import os
import time
from django.conf import settings
from django.db.models import Max
from .models import PlayerScore, PlayerProfile, Game, Leaderboard  # Import models

@login_required
def select_difficulty2(request):
    """Allows the user to choose the game difficulty."""
    if request.method == "POST":
        difficulty = request.POST.get("difficulty")
        if difficulty in ["easy", "medium", "hard"]:
            request.session["difficulty"] = difficulty  # Save difficulty in session
            return redirect("sign_game2")
    return render(request, "recognition/select_difficulty2.html")


@login_required
def sign_game2(request):
    """Main game logic for Sign Matching Game."""
    if "difficulty" not in request.session:
        return redirect("select_difficulty2")

    difficulty = request.session.get("difficulty")
    time_limits = {"easy": 30, "medium": 20, "hard": 10}
    total_time = time_limits.get(difficulty)

    if request.method == "POST":
        score = int(request.POST.get("score", 0))
        round_number = int(request.POST.get("round_number", 1))
        remaining_time = float(request.POST.get("remaining_time", total_time))
        start_time = float(request.POST.get("start_time", time.time()))

        elapsed_time = time.time() - start_time
        remaining_time -= elapsed_time

        if remaining_time <= 0 or round_number >= 10:
            return render(
                request,
                "recognition/score2.html",
                {
                    "score": score,
                    "game_name": "Sign Matching",
                    "difficulty": difficulty,
                },
            )

        selected_option = request.POST.get("selected_option")
        correct_option = request.POST.get("correct_option")
        if selected_option == correct_option:
            score += 1

        round_number += 1
    else:
        score = 0
        round_number = 1
        remaining_time = total_time

    folder_path = os.path.join(settings.BASE_DIR, "recognition/static/overlay_images")
    sign_images = {str(i): f"{i}.jpg" if i == 0 else f"{i:02}.jpg" for i in range(10)}

    current_sign_number = random.choice(list(sign_images.keys()))
    current_sign_file = sign_images[current_sign_number]

    options = random.sample(range(10), 3)
    if int(current_sign_number) not in options:
        options[random.randint(0, 2)] = int(current_sign_number)
    random.shuffle(options)

    return render(
        request,
        "recognition/sign_game2.html",
        {
            "current_sign_file": current_sign_file,
            "options": options,
            "correct_option": current_sign_number,
            "score": score,
            "round_number": round_number,
            "remaining_time": remaining_time,
            "start_time": time.time(),
        },
    )



from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json
import random
import os
import time
from django.conf import settings
from .models import PlayerScore, PlayerProfile, Game, Leaderboard  # Import models


@login_required
def select_difficulty3(request):
    """Allows the user to choose the game difficulty."""
    if request.method == "POST":
        difficulty = request.POST.get("difficulty")
        if difficulty in ["easy", "medium", "hard"]:
            request.session["difficulty"] = difficulty  # ✅ Save difficulty in session
            return redirect("drag_drop_game")  # ✅ Redirect to game
    return render(request, "recognition/select_difficulty3.html")


@login_required
def drag_drop_game(request):
    """Main game logic for Drag and Drop."""
    if "difficulty" not in request.session:
        return redirect("select_difficulty3")

    difficulty = request.session.get("difficulty")
    time_limits = {"easy": 60, "medium": 45, "hard": 30}
    total_time = time_limits.get(difficulty)

    if request.method == "POST":
        score = int(request.POST.get("score", 0))
        return store_score_and_show_results(request, score, "Drag & Drop", difficulty)

    # Prepare game assets
    folder_path = os.path.join(settings.BASE_DIR, "recognition/static/overlay_images")
    sign_images = {str(i): f"{i}.jpg" if i == 0 else f"{i:02}.jpg" for i in range(10)}

    numbers = list(sign_images.keys())
    random.shuffle(numbers)

    return render(
        request,
        "recognition/drag_drop_game.html",
        {
            "sign_images": sign_images,
            "numbers": numbers,
            "remaining_time": total_time,
        },
    )


@login_required
@csrf_exempt
def store_drag_drop_score(request):
    """API to store Drag & Drop game score via AJAX."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            score = int(data.get("score", 0))

            player = PlayerProfile.objects.get(user=request.user)
            game, _ = Game.objects.get_or_create(title="Drag & Drop", difficulty=request.session.get("difficulty", "medium"))

            # Store score in database
            PlayerScore.objects.create(player=player, game=game, score=score)

            # Update leaderboard
            leaderboard_entry, created = Leaderboard.objects.get_or_create(game=game, player=player)
            if score > leaderboard_entry.highest_score:
                leaderboard_entry.highest_score = score
                leaderboard_entry.save()

            return JsonResponse({"message": "Score saved successfully!", "score": score})

        except (json.JSONDecodeError, ValueError):
            return JsonResponse({"error": "Invalid data"}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)


@login_required
def store_score_and_show_results(request, score, game_title, difficulty):
    """Stores the player's score in the database and updates the leaderboard."""
    try:
        player = PlayerProfile.objects.get(user=request.user)
    except PlayerProfile.DoesNotExist:
        return JsonResponse({"error": "Player profile not found"}, status=400)

    # Ensure the game exists
    game, created = Game.objects.get_or_create(title=game_title, difficulty=difficulty)

    # Store the score
    PlayerScore.objects.create(player=player, game=game, score=score)

    # Update leaderboard
    leaderboard_entry, created = Leaderboard.objects.get_or_create(game=game, player=player)
    if score > leaderboard_entry.highest_score:
        leaderboard_entry.highest_score = score
        leaderboard_entry.save()

    return JsonResponse({"message": "Score saved successfully!", "score": score})


@login_required
def score3(request):
    """Display the final score after the game ends."""
    score = request.GET.get("score", 0)
    return render(request, "recognition/score3.html", {"score": score})


@login_required
def speed_challenge_intro(request):
    """
    Displays the introduction page explaining how to play the Speed Challenge game.
    """
    return render(request, "recognition/speed_challenge_intro.html")
