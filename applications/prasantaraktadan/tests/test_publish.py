from django.test import TestCase

from applications.prasantaraktadan import models
from bandhuapp.tests.initiative_program_support import InitiativeProgramTestsMixin


class PrasantaRaktadanProgramTests(InitiativeProgramTestsMixin, TestCase):
    program_key = 'prasantaraktadan'
    models = models
