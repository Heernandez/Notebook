from django import forms

from .models import Book, Leaf


class CoverFileInput(forms.ClearableFileInput):
    template_name = "Book/widgets/cover_input.html"


class BookForm(forms.ModelForm):
    cover_image = forms.ImageField(required=False, widget=CoverFileInput)

    class Meta:
        model = Book
        fields = ("title", "description", "cover_image", "is_public")


class LeafForm(forms.ModelForm):
    class Meta:
        model = Leaf
        fields = ("text",)
        widgets = {
            "text": forms.Textarea(attrs={"rows": 4, "maxlength": 500}),
        }


class LeafImageUploadForm(forms.Form):
    class MultipleFileInput(forms.ClearableFileInput):
        allow_multiple_selected = True

    images = forms.ImageField(
        required=False,
        widget=MultipleFileInput(attrs={"multiple": True}),
    )
