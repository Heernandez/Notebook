from django import forms

from .models import Book, Leaf


class CoverFileInput(forms.ClearableFileInput):
    template_name = "Book/widgets/cover_input.html"


class BookForm(forms.ModelForm):
    cover_image = forms.ImageField(required=False, widget=CoverFileInput)

    class Meta:
        model = Book
        fields = ("title", "category", "description", "cover_image", "is_public")
        widgets = {
            "title": forms.TextInput(attrs={"maxlength": 50}),
            "description": forms.Textarea(attrs={"maxlength": 200}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["title"].required = True
        self.fields["description"].required = True
        self.fields["category"].required = True
        self.fields["category"].empty_label = "Select a category"


class LeafForm(forms.ModelForm):
    content_json = forms.JSONField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = Leaf
        fields = ("content_json",)

    def clean_content_json(self):
        data = self.cleaned_data.get("content_json")
        if not data:
            return {"type": "doc", "content": [{"type": "paragraph"}]}
        return data


class LeafImageUploadForm(forms.Form):
    class MultipleFileInput(forms.ClearableFileInput):
        allow_multiple_selected = True

    images = forms.ImageField(
        required=False,
        widget=MultipleFileInput(attrs={"multiple": True}),
    )
