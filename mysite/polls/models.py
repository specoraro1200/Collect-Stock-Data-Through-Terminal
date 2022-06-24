from django.db import models


class Data(models.Model):
    key = models.AutoField(primary_key=True)
    ticker = models.TextField(blank=True, null=True)
    high = models.DecimalField(blank=True, null=True,decimal_places=2,max_digits=2)
    low = models.DecimalField(blank=True, null=True,decimal_places=2,max_digits=2)
    median = models.DecimalField(blank=True, null=True,decimal_places=2,max_digits=2)
    percentage = models.TextField(blank=True, null=True)
    lastprice = models.DecimalField(blank=True, null=True,decimal_places=2,max_digits=2)
    annalyst = models.DecimalField(blank=True, null=True,decimal_places=2,max_digits=2)
    date = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'data'


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class Favorites(models.Model):
    ticker = models.TextField(blank=True, null=True)
    currentuser = models.ForeignKey(AuthUser, models.DO_NOTHING, db_column='currentuser')

    class Meta:
        managed = False
        db_table = 'favorites'