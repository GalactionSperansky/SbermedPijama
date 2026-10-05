import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("api", "0005_backfill_appointment_slots")]

    operations = [
        migrations.AlterField(
            model_name="appointment",
            name="slot",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="appointment",
                to="api.slot",
            ),
        ),
    ]
