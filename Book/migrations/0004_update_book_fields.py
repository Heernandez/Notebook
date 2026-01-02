from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Book", "0003_remove_book_content"),
    ]

    operations = [
        migrations.AlterField(
            model_name="book",
            name="description",
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name="book",
            name="title",
            field=models.CharField(max_length=50),
        ),
    ]
