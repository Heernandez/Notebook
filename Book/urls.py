from django.urls import path

from . import views

app_name = "Book"

urlpatterns = [
    path("", views.PublicBookListView.as_view(), name="public_list"),
    path("mine/", views.MyBookListView.as_view(), name="my_list"),
    path("new/", views.BookCreateView.as_view(), name="create"),
    path("<int:pk>/", views.BookDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", views.BookUpdateView.as_view(), name="edit"),
    path("<int:pk>/reader/", views.BookReaderView.as_view(), name="reader"),
    path("<int:pk>/add-leaf/", views.LeafCreateView.as_view(), name="add_leaf"),
    path("leaf-editor/upload/", views.leaf_image_upload, name="leaf_image_upload"),
    path("leaves/<int:pk>/edit/", views.LeafUpdateView.as_view(), name="edit_leaf"),
    path("leaf-images/<int:pk>/delete/", views.LeafImageDeleteView.as_view(), name="delete_leaf_image"),
]
