from django.contrib import admin

from .models import Book, Leaf, LeafImage


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "is_public", "updated_at")
    list_filter = ("is_public", "updated_at")
    search_fields = ("title", "description", "content", "owner__username")


@admin.register(Leaf)
class LeafAdmin(admin.ModelAdmin):
    list_display = ("book", "created_at")
    list_filter = ("created_at",)


@admin.register(LeafImage)
class LeafImageAdmin(admin.ModelAdmin):
    list_display = ("leaf", "created_at")
    list_filter = ("created_at",)
