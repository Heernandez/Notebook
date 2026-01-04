from django.db import migrations, models
import django.db.models.deletion


def assign_default_category(apps, schema_editor):
    Category = apps.get_model("categories", "Category")
    Book = apps.get_model("Book", "Book")
    default_category, _ = Category.objects.get_or_create(name="General")
    Book.objects.filter(category__isnull=True).update(category=default_category)


class Migration(migrations.Migration):

    dependencies = [
        ("Book", "0009_savedbook"),
        ("categories", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="book",
            name="category",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="books",
                to="categories.category",
            ),
        ),
        migrations.RunPython(assign_default_category, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="book",
            name="category",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="books",
                to="categories.category",
            ),
        ),
    ]
