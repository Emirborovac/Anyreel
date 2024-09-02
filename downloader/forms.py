from django import forms

class VideoDownloadForm(forms.Form):
    VIDEO_CHOICES = [
        ('1', 'YouTube'),
        ('2', 'Instagram'),
        ('3', 'Other'),
    ]
    video_type = forms.ChoiceField(
        choices=VIDEO_CHOICES,
        label="What video are you downloading?",
        widget=forms.Select(attrs={'class': 'select-menu'})
    )
    url = forms.URLField(
        label="Video URL",
        required=True,
        widget=forms.URLInput(attrs={'class': 'input-field'})
    )
