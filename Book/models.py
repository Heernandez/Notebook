from django.conf import settings
from django.db import models


class Book(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="books",
    )
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=200, blank=True)
    cover_image = models.ImageField(upload_to="books/covers/", blank=True, null=True)
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self) -> str:
        return self.title


class Leaf(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="leaves")
    text = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Leaf for {self.book.title}"


class LeafImage(models.Model):
    leaf = models.ForeignKey(Leaf, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="books/leaves/")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"Leaf image {self.leaf_id}"
