from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Book", "0007_alter_book_id_alter_leaf_id_alter_leafimage_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="leaf",
            name="content_json",
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
