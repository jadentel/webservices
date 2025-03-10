from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from django.db.models import Avg
from .models import Professor, Module, ModuleInstance, Rating
from .serializers import ModuleInstanceSerializer

# Reference - https://www.django-rest-framework.org/api-guide/authentication/
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    username = request.data.get('username')
    email= request.data.get('email')
    password = request.data.get('password')
    if not username or not email or not password:
        return Response({'error': 'Please provide username, email, and password.'}, status=status.HTTP_400_BAD_REQUEST)
    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already exists, try logging in.'}, status=status.HTTP_400_BAD_REQUEST)
    user= User(username=username, email=email)
    user.set_password(password)
    user.save()
    return Response({'message': 'User registered successfully. '}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    if user is not None:
        token, created = Token.objects.get_or_create(user=user)
        return Response({'message': 'Login successful.', 'token': token.key}, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Invalid credentials.'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    request.user.auth_token.delete()
    return Response({'message': 'Logout successful.'}, status=status.HTTP_200_OK)

@api_view(['GET'])
def list_module_instances(request):
    instances = ModuleInstance.objects.all()
    serializer = ModuleInstanceSerializer(instances, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def list_professors(request):
    professors = Professor.objects.all()
    result=[]
    for prof in professors:
        average_rating = Rating.objects.filter(professor=prof).aggregate(avg=Avg('rating'))['avg']
        if average_rating is not None:
            # to ensure that it turns it to an integer to better represent the stars.
            average_rating = round(average_rating)
        else:
            average_rating = 0
        result.append({'professor_id': prof.professor_id, 'name': prof.name, 'average_rating': average_rating})
    return Response(result, status=status.HTTP_200_OK)

@api_view(['GET'])
def average_rating(request):
    professor_id = request.query_params.get('professor_id')
    module_code = request.query_params.get('module_code')
    if not professor_id or not module_code:
        return Response({'error': 'Provide professor_id and module_code as query parameters.'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        professor = Professor.objects.get(professor_id=professor_id)
    except Professor.DoesNotExist:
        return Response({'error': 'Professor not found.'}, status=status.HTTP_404_NOT_FOUND)
    try:
        module = Module.objects.get(code=module_code)
    except Module.DoesNotExist:
        return Response({'error': 'Module not found.'}, status=status.HTTP_404_NOT_FOUND)
    

    instances = ModuleInstance.objects.filter(module=module, professors=professor)
    ratings = Rating.objects.filter(professor=professor, module_instance__in=instances)
    avg_rating = ratings.aggregate(avg=Avg('rating'))['avg']
    if avg_rating is not None:
        avg_rating = round(avg_rating)
    else:
        avg_rating = 0
    return Response({'professor_id': professor.professor_id, 'module_code': module.code, 'average_rating': avg_rating}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def rate_professor(request):
    professor_id = request.data.get('professor_id')
    module_code = request.data.get('module_code')
    year = request.data.get('year')
    semester = request.data.get('semester')
    rating_value = request.data.get('rating')

    if not (professor_id and module_code and year and semester and rating_value):
        return Response({'error': 'Missing professorID/year/semester/rating.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        professor = Professor.objects.get(professor_id=professor_id)
    except Professor.DoesNotExist:
        return Response({'error': 'Professor not found.'}, status=status.HTTP_404_NOT_FOUND)

    try:
        module = Module.objects.get(code=module_code)
    except Module.DoesNotExist:
        return Response({'error': 'Module not found.'}, status=status.HTTP_404_NOT_FOUND)

    try:
        instance = ModuleInstance.objects.get(module=module, year=year, semester=semester)
    except ModuleInstance.DoesNotExist:
        return Response({'error': 'Module instance not found.'}, status=status.HTTP_404_NOT_FOUND)

    if not instance.professors.filter(id=professor.id).exists():
        return Response({'error': 'Professor does not teach in this module instance.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        rating_value = int(rating_value)
        if rating_value < 1 or rating_value > 5:
            raise ValueError
    except ValueError:
        return Response({'error': 'Rating must be an integer between 1 and 5.'}, status=status.HTTP_400_BAD_REQUEST)

    # Check if a rating already exists for this user, professor, and module instance
    if Rating.objects.filter(user=request.user, professor=professor, module_instance=instance).exists():
        return Response({'error': 'Rating already submitted for this module instance and cannot be updated.'}, status=status.HTTP_400_BAD_REQUEST)

    # Creating new rating
    Rating.objects.create(user=request.user, professor=professor, module_instance=instance, rating=rating_value
    )
    return Response({'message': 'Rating submitted successfully.'}, status=status.HTTP_200_OK)