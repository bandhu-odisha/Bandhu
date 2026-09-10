from django.test import TestCase

from applications.patriotism import models
from bandhuapp.tests.initiative_program_support import InitiativeProgramTestsMixin


class PatriotismProgramTests(InitiativeProgramTestsMixin, TestCase):
    program_key = 'patriotism'
    models = models
