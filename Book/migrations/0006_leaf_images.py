from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("Book", "0005_update_leaf_text_length"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="leaf",
            name="image",
        ),
        migrations.CreateModel(
            name="LeafImage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("image", models.ImageField(upload_to="books/leaves/")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "leaf",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="images", to="Book.leaf"),
                ),
            ],
            options={
                "ordering": ["created_at"],
            },
        ),
    ]
