from django import forms


class ContactForm(forms.Form):
    name = forms.CharField(max_length=200, widget=forms.TextInput(attrs={
        'placeholder': 'Your Name'
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'placeholder': 'Your Email'
    }))
    message = forms.CharField(widget=forms.Textarea(attrs={
        'placeholder': 'Your Message', 'rows': 5
    }))


class SupportForm(forms.Form):
    subject = forms.CharField(max_length=255, initial='App Support')
    description = forms.CharField(widget=forms.Textarea(attrs={'rows': 5}))
    priority = forms.ChoiceField(choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('urgent', 'Urgent')], initial='medium')
