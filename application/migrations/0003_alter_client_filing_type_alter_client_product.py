# Generated by Django 5.1.3 on 2024-12-01 07:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("application", "0002_alter_client_tin_alter_client_created_at_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="client",
            name="filing_type",
            field=models.CharField(
                blank=True,
                choices=[
                    ("", ""),
                    ("Simple", "Simple"),
                    ("Credits", "Credits"),
                    ("Itemizing", "Itemizing"),
                    ("Sole Proprietor", "Sole Proprietor"),
                    ("Corporation", "Corporation"),
                ],
                default="",
                max_length=100,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="client",
            name="product",
            field=models.CharField(
                blank=True,
                choices=[
                    ("", ""),
                    ("Personal Taxes", "Personal Taxes"),
                    ("Corporate Taxes", "Corporate Taxes"),
                    ("Extension", "Extension"),
                    ("Amendment", "Amendment"),
                    ("Withholdings Adjustment", "Withholdings Adjustment"),
                    ("Advisory", "Advisory"),
                    ("Reject Correction", "Reject Correction"),
                ],
                default="",
                max_length=100,
                null=True,
            ),
        ),
    ]
