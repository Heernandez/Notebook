from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("Book", "0002_leaf"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="book",
            name="content",
        ),
    ]
