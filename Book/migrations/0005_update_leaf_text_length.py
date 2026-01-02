from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Book", "0004_update_book_fields"),
    ]

    operations = [
        migrations.AlterField(
            model_name="leaf",
            name="text",
            field=models.CharField(blank=True, max_length=500),
        ),
    ]
