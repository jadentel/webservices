from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Professor, Module, ModuleInstance, Rating

# Reference - https://www.django-rest-framework.org/api-guide/serializers/

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email']

class ProfessorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Professor
        fields = ['professor_id', 'name']

class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ['code', 'name']

class ModuleInstanceSerializer(serializers.ModelSerializer):
    module_code = serializers.CharField(source='module.code', read_only=True)
    module_name = serializers.CharField(source='module.name', read_only=True)
    professors = ProfessorSerializer(many=True, read_only=True)

    class Meta:
        model = ModuleInstance
        fields = ['module_code', 'module_name', 'year', 'semester', 'professors']

class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ['user', 'professor', 'module_instance', 'rating']
