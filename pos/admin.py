from django.contrib import admin

# Register your models here.
from .models import Pos_data,Pos_word,QuizQuestion,QuizAns,Score

admin.site.register(Pos_data)
admin.site.register(Pos_word)
admin.site.register(QuizQuestion)
admin.site.register(QuizAns)
admin.site.register(Score)
