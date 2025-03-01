from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Pos_data(models.Model):
    host = models.ForeignKey(User,on_delete=models.CASCADE)
    sentance = models.TextField(max_length=1000)

class Pos_word(models.Model):
    sentance = models.ForeignKey(Pos_data,on_delete=models.CASCADE)
    word = models.CharField(max_length= 15)
    tag = models.CharField(max_length=15)

class QuizQuestion(models.Model):
    sentance = models.CharField(max_length=1500)
    word = models.CharField(max_length=120,default="Error")
    def __str__(self):
        return self.sentance
class QuizChoice(models.Model):
    sentance = models.ForeignKey(QuizQuestion,on_delete = models.CASCADE)
    choice = models.CharField(max_length=150)
    def __str__(self):
        return self.chocie
class QuizAns(models.Model):
    sentance = models.ForeignKey(QuizQuestion,on_delete = models.CASCADE)
    answer = models.CharField(max_length=150)
    def __str__(self):
        return self.answer

class Score(models.Model):
    Host = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100 ,default="None")
    score = models.IntegerField(default=0)
    def __str__(self):
        return self.name