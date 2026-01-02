from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("Book", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Leaf",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("text", models.TextField(blank=True)),
                ("image", models.ImageField(blank=True, null=True, upload_to="books/leaves/")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "book",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="leaves", to="Book.book"),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
    ]
