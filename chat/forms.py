from django import forms
from .choices import MODEL_CHOICES, RESPONSE_MODE_CHOICES

class ChatForm(forms.Form):
    message = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        max_length=2000,
        required=False,
        label=""
    )
    model_choice = forms.ChoiceField(
        choices=MODEL_CHOICES,
        required=False,
        widget=forms.Select(),
        label="モデル選択",
        initial='gpt-3.5-turbo'
    )
    response_mode = forms.ChoiceField(
        choices=RESPONSE_MODE_CHOICES,
        required=False,
        widget=forms.Select(),
        label="返答モード",
        initial='free'
    )