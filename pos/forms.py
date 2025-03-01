from django.forms import ModelForm
from .models import Pos_data,Pos_word

class PosDataForm(ModelForm):
    class Meta:
        model = Pos_data
        fields = "__all__"
        exclude = ["host"]

# class PosWordForm(ModelForm):
#     class Meta:
#         model = Pos_word
#         fields = "__all__"
