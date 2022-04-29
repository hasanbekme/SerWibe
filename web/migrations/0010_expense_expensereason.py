# Generated by Django 3.2.13 on 2022-04-27 11:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0009_auto_20220427_1207'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExpenseReason',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50, verbose_name='Nomi')),
            ],
        ),
        migrations.CreateModel(
            name='Expense',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Sanasi')),
                ('amount', models.IntegerField(verbose_name='Sarflangan summa')),
                ('performer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.worker')),
                ('reason', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.expensereason')),
            ],
        ),
    ]