from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg, Q
import os
import uuid

from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DetailView, ListView, UpdateView
from django.core.files.storage import default_storage

from .forms import BookForm, LeafForm, LeafImageUploadForm
from .models import Book, Leaf, LeafImage, SavedBook
from reviews.models import Review


class PublicBookListView(ListView):
    model = Book
    template_name = "Book/public_list.html"
    context_object_name = "books"

    def get_queryset(self):
        query = self.request.GET.get("q", "").strip()
        category_id = self.request.GET.get("category", "").strip()
        qs = Book.objects.filter(is_public=True).annotate(
            avg_rating=Avg("reviews__rating")
        )
        if category_id:
            qs = qs.filter(category_id=category_id)
        if query:
            qs = qs.filter(
                Q(title__icontains=query)
                | Q(description__icontains=query)
            )
        return qs


class MyBookListView(LoginRequiredMixin, ListView):
    model = Book
    template_name = "Book/my_list.html"
    context_object_name = "books"

    def get_queryset(self):
        qs = Book.objects.filter(owner=self.request.user)
        query = self.request.GET.get("q", "").strip()
        category_id = self.request.GET.get("category", "").strip()
        if category_id:
            qs = qs.filter(category_id=category_id)
        if query:
            qs = qs.filter(
                Q(title__icontains=query)
                | Q(description__icontains=query)
            )
        return qs.annotate(
            avg_rating=Avg("reviews__rating")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["saved_books"] = (
            Book.objects.filter(saved_by__user=self.request.user)
            .exclude(owner=self.request.user)
            .annotate(avg_rating=Avg("reviews__rating"))
            .distinct()
        )
        return context


class BookDetailView(DetailView):
    model = Book
    template_name = "Book/detail.html"
    context_object_name = "book"

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
        except Http404:
            requested_id = kwargs.get("pk")
            context = {
                "book_missing": True,
                "requested_id": requested_id,
            }
            return render(request, "Book/detail.html", context, status=404)
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Book.objects.filter(
                Q(is_public=True) | Q(owner=self.request.user)
            )
        return Book.objects.filter(is_public=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = self.request.GET.get("order", "newest")
        ordering = "created_at" if order == "oldest" else "-created_at"
        context["leaves"] = Leaf.objects.filter(book=self.object).order_by(ordering)
        context["leaf_order"] = order
        context["reviews"] = (
            Review.objects.filter(book=self.object)
            .select_related("user")
            .prefetch_related("user__socialaccount_set")
            .order_by("-rating", "-created_at")[:3]
        )
        rating_qs = Review.objects.filter(book=self.object)
        rating_data = rating_qs.aggregate(avg_rating=Avg("rating"))
        context["avg_rating"] = rating_data["avg_rating"]
        context["review_count"] = rating_qs.count()
        if self.request.user.is_authenticated:
            context["is_saved"] = SavedBook.objects.filter(
                user=self.request.user, book=self.object
            ).exists()
        else:
            context["is_saved"] = False
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not request.user.is_authenticated:
            return redirect("account_login")
        rating_raw = request.POST.get("rating", "").strip()
        comment = request.POST.get("comment", "").strip()
        rating = None
        if rating_raw.isdigit():
            rating = int(rating_raw)
        if not comment or rating is None or rating < 1 or rating > 5:
            context = self.get_context_data(object=self.object)
            context["review_error"] = "Please add a rating and a short comment."
            context["review_comment"] = comment
            context["review_rating"] = rating_raw
            return self.render_to_response(context, status=400)
        Review.objects.create(
            book=self.object,
            user=request.user,
            rating=rating,
            comment=comment,
        )
        return redirect("Book:detail", pk=self.object.pk)


class BookReaderView(BookDetailView):
    template_name = "Book/reader.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["hide_topbar"] = True
        context["leaves"] = Leaf.objects.filter(book=self.object).order_by("created_at")
        context["leaf_order"] = "oldest"
        return context


class BookCreateView(LoginRequiredMixin, CreateView):
    model = Book
    template_name = "Book/form.html"
    form_class = BookForm
    success_url = reverse_lazy("Book:my_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class BookUpdateView(LoginRequiredMixin, UpdateView):
    model = Book
    template_name = "Book/form.html"
    form_class = BookForm
    success_url = reverse_lazy("Book:my_list")

    def get_queryset(self):
        return Book.objects.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["leaf_form"] = LeafForm()
        context["leaves"] = Leaf.objects.filter(book=self.object)
        return context


class LeafCreateView(LoginRequiredMixin, CreateView):
    model = Leaf
    form_class = LeafForm
    template_name = "Book/leaf_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.book = Book.objects.filter(
            pk=kwargs.get("pk"), owner=request.user
        ).first()
        if not self.book:
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)
        except Http404:
            requested_id = kwargs.get("pk")
            context = {
                "book_missing": True,
                "requested_id": requested_id,
            }
            return render(request, "Book/leaf_form.html", context, status=404)

    def form_valid(self, form):
        form.instance.book = self.book
        response = super().form_valid(form)
        images = self.request.FILES.getlist("images")
        for image in images:
            LeafImage.objects.create(leaf=self.object, image=image)
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["book"] = self.book
        context["image_form"] = LeafImageUploadForm()
        return context

    def get_success_url(self):
        return reverse_lazy("Book:detail", kwargs={"pk": self.book.pk})


class LeafUpdateView(LoginRequiredMixin, UpdateView):
    model = Leaf
    form_class = LeafForm
    template_name = "Book/leaf_edit.html"

    def get_queryset(self):
        return Leaf.objects.filter(book__owner=self.request.user)

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
        except Http404:
            requested_id = kwargs.get("pk")
            context = {
                "leaf_missing": True,
                "requested_id": requested_id,
            }
            return render(request, "Book/leaf_edit.html", context, status=404)
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["image_form"] = LeafImageUploadForm()
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        images = self.request.FILES.getlist("images")
        for image in images:
            LeafImage.objects.create(leaf=self.object, image=image)
        return response

    def get_success_url(self):
        return reverse_lazy("Book:detail", kwargs={"pk": self.object.book.pk})


class LeafImageDeleteView(LoginRequiredMixin, DetailView):
    model = LeafImage

    def post(self, request, *args, **kwargs):
        image = LeafImage.objects.filter(
            pk=kwargs.get("pk"), leaf__book__owner=request.user
        ).first()
        if not image:
            raise Http404
        leaf_id = image.leaf_id
        image.delete()
        return redirect("Book:edit_leaf", pk=leaf_id)


@login_required
@require_POST
def toggle_saved_book(request, pk):
    book = Book.objects.filter(pk=pk).filter(
        Q(is_public=True) | Q(owner=request.user)
    ).first()
    if not book:
        raise Http404
    saved_entry, created = SavedBook.objects.get_or_create(
        user=request.user, book=book
    )
    if created:
        is_saved = True
    else:
        saved_entry.delete()
        is_saved = False
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"saved": is_saved})
    return redirect("Book:detail", pk=book.pk)


@login_required
@require_POST
def leaf_image_upload(request):
    file = request.FILES.get("image")
    if not file:
        return JsonResponse({"error": "Missing image"}, status=400)
    _, ext = os.path.splitext(file.name)
    name = f"books/leaf_editor/{uuid.uuid4().hex}{ext.lower()}"
    path = default_storage.save(name, file)
    return JsonResponse({"url": default_storage.url(path)})
