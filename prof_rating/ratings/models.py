from django.db import models
from django.contrib.auth.models import User

class Professor(models.Model):
    professor_id = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.professor_id} - {self.name}"

class Module(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.code} - {self.name}"

class ModuleInstance(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    year = models.IntegerField()  # e.g., 2018 for academic year 2018-19
    semester = models.IntegerField()
    professors = models.ManyToManyField(Professor)

    def __str__(self):
        return f"{self.module.code} {self.module.name} ({self.year}, Sem {self.semester})"

class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE)
    module_instance = models.ForeignKey(ModuleInstance, on_delete=models.CASCADE)
    rating = models.IntegerField()  # Value between 1 and 5

    class Meta:
        unique_together = ('user', 'professor', 'module_instance')
