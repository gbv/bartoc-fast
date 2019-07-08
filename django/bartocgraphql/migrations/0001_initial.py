# Generated by Django 2.2 on 2019-07-05 12:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Federation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='SkosmosInstance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('url', models.URLField()),
                ('timeout', models.BooleanField(blank=True)),
                ('federation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bartocgraphql.Federation')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SparqlEndpoint',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('url', models.URLField()),
                ('timeout', models.BooleanField(blank=True)),
                ('federation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bartocgraphql.Federation')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SparqlQuery',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('querystring', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=100)),
                ('category', models.IntegerField()),
                ('timeout', models.BooleanField()),
                ('sparqlendpoint', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bartocgraphql.SparqlEndpoint')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SkosmosQuery',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('querystring', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=100)),
                ('category', models.IntegerField()),
                ('timeout', models.BooleanField()),
                ('skosmosinstance', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bartocgraphql.SkosmosInstance')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
