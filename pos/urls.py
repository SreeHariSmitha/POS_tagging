from django.urls import path
from . import views

urlpatterns = [
    path('',views.home,name = "home"),
    path("login",views.view_login,name = "login"),
    path("register",views.registerPage,name = "register"),
    path("postagger",views.posTagger,name = "posTagger"),
    path("postaggerans/<str:sentance>",views.posTaggerAnswer,name = "posTaggerAnswer"),
    path('log_out/',views.log_out,name = "log_out"),
    path("quiz/",views.QuizApp,name = "quiz"),
    path("leaderboard/",views.leaderBoard,name = "leaderboard")

]