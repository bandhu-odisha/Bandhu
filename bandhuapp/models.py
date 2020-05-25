from django.db import models
from accounts.models import User
# Create your models here.

class Profile(models.Model):
    email = models.EmailField()
    full_name = models.CharField(max_length=350)
    phone = models.CharField(max_length=12)
    address = models.CharField(max_length=500)
    city = models.CharField(max_length=350)
    profession = models.CharField(max_length=500)
    dob = models.DateTimeField()

    def __str__(self):
        return self.full_name

class Charity(models.Model):
	name = models.CharField(max_length=350)
	description = models.TextField(max_length=1000)
	# charity_type = models.choices(CHARITY_TYPES)
	# amount = models.IntegerField(min=0)
	date = models.DateTimeField()
	address = models.CharField(max_length=350)
	city = models.CharField(max_length=100)

	def __str__(self):
		return self.name

class Activity(models.Model):
	title = models.CharField(max_length=350)
	description = models.TextField(max_length=1000)
	theme = models.CharField(max_length=100)
	guest = models.CharField(max_length=100)
	winners = models.TextField(max_length=500)
	# location = models.ForeignKey() 
	# photos = models.ForeignKey()

	def __str__(self):
		return self.title

class Meeting(models.Model):
	title = models.CharField(max_length=350)
	# minutes_of_meeting = some models / plain text field
	date = models.DateTimeField()
	# location = models.ForeignKey()
	
	def __str__(self):
		return self.title

class Ashram(models.Model):
	name = models.CharField(max_length=350)
	address = models.CharField(max_length=350)
	est_date = models.DateTimeField() #established date
	description = models.TextField(max_length=1000)

	def __str__(self):
		return self.name


# class Ankurayan(models.Model):
#     ankurayan_activity = models.ForeignKey()
#     #some other fields

# class Ankurayan_activity(models.Model):
#     title = models.CharField(max_length=350)
#     description = models.TextField(max_length=1000)
#     date = models.DateTimeField()

#     def __str__(self):
		# return self.title

# class Photo(models.model)
