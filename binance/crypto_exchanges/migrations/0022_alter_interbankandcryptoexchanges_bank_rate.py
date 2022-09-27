# Generated by Django 3.2.14 on 2022-09-26 16:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('banks', '0009_remove_bestbankexchangesupdates_bank'),
        ('crypto_exchanges', '0021_interbankandcryptoexchanges_interbankandcryptoexchangesupdates'),
    ]

    operations = [
        migrations.AlterField(
            model_name='interbankandcryptoexchanges',
            name='bank_rate',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bank_rate_inter_bank_and_crypro_exchanges', to='banks.bestbankexchanges'),
        ),
    ]
