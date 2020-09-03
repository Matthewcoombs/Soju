from django.forms import ModelForm, TextInput

from .models import UserID

class UserIDForm(ModelForm):
    class Meta:
        model = UserID
        fields = ['userID']
        widgets = {'userID' : TextInput(attrs={'class' : 'input', 'placeholder': 'userID_input'})}