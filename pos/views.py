from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from .forms import PosDataForm
from .models import Pos_data,Pos_word,QuizQuestion,QuizChoice,QuizAns,Score
from django.contrib.auth.decorators import login_required
import random
import pandas as pd
import numpy as np 
emmision_data = pd.read_csv("static/csv_files/emmision_table_probability_lower_final.csv", index_col=0)
transition_data = pd.read_csv("static/csv_files/transition_table_probability_total.csv", index_col=0)
tags = ['NOUN', '.', 'NUM', 'ADJ', 'VERB', 'DET', 'ADP', 'CONJ', 'X', 'ADV', 'PRT', 'PRON']
initial_probabilities = { 'NOUN': 0.1621, '.': 0.0536, 'NUM': 0.0192, 'ADJ': 0.0426,
                         'VERB': 0.0437, 'DET': 0.2438, 'ADP': 0.1429, 'CONJ': 0.0502, 'X': 0.0024,
                         'ADV': 0.0898, 'PRT': 0.0286, 'PRON': 0.1211}

# Create your views here.


def home(request):
    data = None
    form = PosDataForm()
    # context = {}
    if request.user.is_authenticated:
        data  = Pos_data.objects.filter(host = request.user)
    else:
        if request.method =="POST":
            sentance = request.POST.get("sentance")
            words = sentance.split()

            print(words)
            tags,_ = viterbi_algorithm(words)
            tags = tagChangeFull(tags)
            temp = []
            for word,tag in zip(words,tags):
                temp.append((word,tag))
            context = {"words_tags":temp,"sentance":sentance,"data":None}
            return render(request,"pos/posTagger_answer.html",context)
    
    if request.method == 'POST':
        form = PosDataForm(request.POST)
        sentance = request.POST.get("sentance").rstrip()
        print(sentance)
        if not Pos_data.objects.filter(sentance=sentance).exists():
            print("you are awesome")
            if form.is_valid():
                form = form.save(commit = False)
                form.host = request.user
                form.save()
                return redirect("posTaggerAnswer",sentance)
        else:
            return redirect("posTaggerAnswer",sentance)
        
    context = {"form":form,"data":data}
    return render(request, 'pos/home.html',context)


def view_login(request):
    if request.method == "POST":
        username = request.POST.get("username").lower()
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            return redirect("home")
        
    return render(request, "pos/login_register.html")


def log_out(request):
    logout(request)
    return redirect('home')


def registerPage(request):
    form = UserCreationForm()
    print(form)
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        print(form)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            Score.objects.create(Host = user,name = user.username.lower() )
            login(request, user)
            return redirect('home')

    context = {"form": form}
    return render(request, "pos/register.html", context)

@login_required(login_url="login")
def posTagger(request):
    form = PosDataForm()
    if request.method == 'POST':
        form = PosDataForm(request.POST)

        sentance = request.POST.get("sentance").rstrip()
        if not Pos_data.objects.filter(sentance=sentance).exists():
            if form.is_valid():
                form = form.save(commit = False)
                form.host = request.user
                form.save()
                return redirect("posTaggerAnswer",sentance)
        else:
            return redirect("posTaggerAnswer",sentance)

    context = {"form": form}
    return render(request, 'pos/posTagger.html',context)



def posTaggerAnswer(request,sentance):  

    wordSeq,acc = viterbi_algorithm(sentance.split())
    data  = Pos_data.objects.filter(host = request.user)
    print(wordSeq)
    wordSeq= tagChangeFull(wordSeq)
    for word,tag in zip(sentance.split(),wordSeq):

        Pos_word.objects.create(sentance = Pos_data.objects.get(sentance = sentance),word = word,tag = tag)

    context = {"sentance":sentance,"words_tags":zip(sentance.split(" "),wordSeq),"data": data}
    return render(request,"pos/posTagger_answer.html",context)


def posTaggerShow(request,sentance):
    wordTags = Pos_word.objects.get(sentance= "sentance")
    data  = Pos_data.objects.filter(host = request.user)
    allWordTag=[]
    for wordTag in wordTags:
        allWordTag.append(wordTag.word,wordTag.tags)
    context = {"sentance":sentance,"words_tags":allWordTag,"data": data}
    return render(request,"pos/posTagger_answer.html",context)

def QuizApp(request):
    if request.method == 'POST':
        # print("POST",request.POST.get("choice"),answer)
        if request.POST.get("choice") == request.POST.get("answer"):
            user_data = Score.objects.get(Host = request.user)
            user_data.score=user_data.score+1
            user_data.save()
    ques_num = random.randint(0,2000)
    data= QuizQuestion.objects.get(id = ques_num)
    answer = QuizAns.objects.get(sentance = data)
    options = ["Noun","Punctuation","Number","Adjoint","Verb","Article","Preposition","Conjunction","Unknown","Adverb","Particle","Pronoun"] 
    choices = [answer.answer]
    while len(choices)!=4:
        ansId = random.randint(0,8)
        print(options[ansId],choices)
        # print(choices)
        if options[ansId] not in choices:
            choices.append(options[ansId])
    random.shuffle(choices)
    print(data.sentance)
    print(answer)
    score = Score.objects.get(name = request.user)

    context = {"question":data.sentance,"choices":choices,"ques_word":data.word,"answer":answer,"score":score.score}
    return render(request,"pos/quizApp.html",context)

def leaderBoard(request):
    mydata = Score.objects.all().order_by('-score').values()
    data = []
    c=1
    for i in mydata:
        data.append((c,i["name"],i["score"]))
        c+=1
    
    context = {"mydata":data}
    return render(request,"pos/leaderBoard.html",context)

def tagChangeFull(tags):
    short_names= ['NOUN', '.', 'NUM', 'ADJ', 'VERB', 'DET', 'ADP', 'CONJ', 'X', 'ADV', 'PRT', 'PRON']
    full_names = ["Noun","Punctuation","Number","Adjective","Verb","Article","Preposition","Conjunction","Unknown","Adverb","Particle","Pronoun"] 
    final_list = []
    for tag  in tags:
        ind = short_names.index(tag)
        final_list.append(full_names[ind])
    return final_list

def tagChangeFullforword(tag):
    short_names= ['NOUN', '.', 'NUM', 'ADJ', 'VERB', 'DET', 'ADP', 'CONJ', 'X', 'ADV', 'PRT', 'PRON']
    full_names = ["Noun","Punctuation","Number","Adjective","Verb","Article","Preposition","Conjunction","Unknown","Adverb","Particle","Pronoun"] 
    # final_list = []
    # for tag  in tags:
    ind = short_names.index(tag)
    return full_names[ind]
    # return final_list

def viterbi_algorithm(obs_seq):
    m = len(obs_seq)
    n = len(tags)
    V = np.zeros((m, n))
    if obs_seq[0].lower() in emmision_data.index:
        emi_pro = emmision_data.loc[obs_seq[0].lower()]
    else:
        emi_pro = [0.6302382498376704, 0.0005494231057389741, 0.09674841416512661, 0.1257679436591579, 0.106038659407622, 0.00034963288547025626, 0.0010488986564107688, 0.0003995804405374357, 0.008241346586084611, 0.02117776334848409, 0.009190350132361021,0.0002497377753358973]
    for i in range(n):
        V[0][i] = initial_probabilities[tags[i]] * emi_pro[i]

    for j in range(1, m):
        
        if obs_seq[j].lower() in emmision_data.index:
            emi_pro = emmision_data.loc[obs_seq[j].lower()]
        else:
            emi_pro = [0.6302382498376704, 0.0005494231057389741, 0.09674841416512661, 0.1257679436591579, 0.106038659407622, 0.00034963288547025626, 0.0010488986564107688, 0.0003995804405374357, 0.008241346586084611, 0.02117776334848409, 0.009190350132361021,0.0002497377753358973]
        for k in range(n):
            max_prob = 0.0
            max_index = 0
            for l in range(n):
                prob = V[j - 1][l] * transition_data.loc[tags[l], tags[k]] * emi_pro[k]
                if prob > max_prob:
                    max_prob = prob
                    max_index = l
            V[j][k] = max_prob
    # Termination step 
    b = max(V[m - 1])  
    best_last_state = np.argmax(V[m - 1])

    best_path_states = [np.argmax(V[t]) for t in range(m)] # stores best  index fr each time

    # Convert the indices to the corresponding POS tags
    best_path = [tags[state] for state in best_path_states]

    return best_path, b

# # ---------------------------------------------------------------------
# import nltk
# import nltk.corpus as nltkc

 
# treebank_corpus = nltkc.treebank.tagged_sents(tagset='universal')
# # brown_corpus = nltkc.brown.tagged_sents(tagset='universal')
# # conll_corpus = nltkc.conll2000.tagged_sents(tagset='universal')

# # #joining all the 3 data 
# # nltk_data = treebank_corpus + brown_corpus + conll_corpus
# nltk_data = list(treebank_corpus[:2000])
# options = ["NOUN","ADJ","VERB","DET","ADP","CONJ","ADV","PRT","PRON"]

# for sentance in nltk_data:
#     sentance_correct = []
#     ind = random.randint(1,len(sentance))
#     ans_ind = 0
#     got_ans = False
#     for word,tag in sentance:
#         ans_ind+=1
#         if tag not in [".","X","NUM"]:
#             if ans_ind>ind and not got_ans:
#                 # print(tag)
#                 # here i will store the answere in database 
#                 # print(tag)
#                 tag = tagChangeFullforword(tag)
#                 # print(word,tag)
#                 queWord,queTag = word,tag
#                 got_ans = True  
#         if tag != "X":
#             sentance_correct.append(word)
    

#     if got_ans == False:
#         for word,tag in sentance:
#             if tag not in [".","X","NUM"] and not got_ans:
#                 # here i will store the answere in database
#                 print(tag)
#                 tag = tagChangeFullforword(tag)
#                 print(tag)
#                 queWord,queTag = word,tag
#                 # print(word,tag)
#                 got_ans = True
#     # QuizQuestion.objects.create(sentance=" ".join(sentance_correct),word ="")

#     QuizAns.objects.create(sentance = QuizQuestion.objects.create(sentance=" ".join(sentance_correct),word =queWord) ,answer =queTag )
#     # print(sentance)
# print("------------Done!------------")



# # ---------------------------------------------------------------------