from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.conf import settings
from .models import PredictionData 
from django.contrib.auth.hashers import make_password
from collections import Counter
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.utils import timezone
from django.db.models import Count
from django.contrib.auth.models import User
from django.db.models import Count
from django.shortcuts import render
from .models import PredictionData
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import joblib
import os

def logout_view(request):
    logout(request)
    return redirect('login')

def landing_page(request):
    return render(request, 'landing_page.html')

@login_required
def output_view(request):
    return render(request, 'output.html')
@login_required
def about_view(request):
    return render(request, 'about.html')
@login_required
def our_team_view(request):
    return render(request, 'our_team.html')
@login_required
def home_view(request):
    return render(request, 'home.html')
@login_required
def contact_us_view(request):
    return render(request, 'contact_us.html')
@login_required
def predict_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        sex = request.POST.get('sex')
        age = int(request.POST.get('age'))
        weight = float(request.POST.get('weight'))
        height = float(request.POST.get('height'))
        sex_encoded = 1 if sex.lower() == 'female' else 0
        model_path = os.path.join(settings.BASE_DIR, 'WebApp', 'models', 'NUTRITIONAL_STATUS.pkl')
        model = joblib.load(model_path)
        input_data = [[sex_encoded, weight, height, age]]
        nutritional_probabilities = model.predict_proba(input_data)
        nutritional_probabilities_list = nutritional_probabilities[0].tolist()
        prediction_result = model.predict(input_data)[0]
        nutritional_status_mapping = {0: 'Moderately Wasted', 1: 'Normal', 2: 'Over Weight', 3: 'Obese', 4: 'Severely Wasted'}
        predicted_label = nutritional_status_mapping.get(prediction_result, 'Unknown')
        percentage_probabilities = [round(prob * 100, 2) for prob in nutritional_probabilities_list] 
        disclaimer = "Disclaimer : The information presented here is based on predicted nutritional status and may not be entirely accurate. "
        PredictionData.objects.create(
             user=request.user,
            name=name.upper(),
            sex=sex.upper(),
            age=age,
            weight=weight,
            height=height,
            prediction_result=predicted_label
            ) 
        return render(request, 'output.html', {
            'name': name.upper(),
            'sex': sex.upper(),
            'age': age,
            'weight': weight,
            'height': height,
            'result': predicted_label,
            'probabilities': percentage_probabilities,
            'disclaimer': disclaimer,
        })
    else:
        return render(request, 'predict.html')

def sign_up(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return redirect('signup')
        if User.objects.filter(username__iexact=username).exists() or User.objects.filter(email__iexact=email).exists():
            messages.error(request, 'Username or email is already in use.')
            return redirect('signup')
        user = User.objects.create(username=username, email=email, password=make_password(password1))
        user.save()
        messages.success(request, 'Account created successfully. You can now log in.')
        
        user = authenticate(request, username=username, password=password1)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return redirect('login')
    else:
        return render(request, 'sign_up.html')
    
    
def log_in_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')     
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful.')
            return redirect('home')
        else:
            messages.error(request, 'Invalid email or password.')
            return redirect('login')
    return render(request, 'log_in.html')

from django.db.models import Q
@login_required
def dashboard(request):
    predictions = PredictionData.objects.filter(user=request.user) 
    search_query = request.GET.get('q', '')
    if search_query:
        predictions = predictions.filter(
            Q(name__icontains=search_query) |
            Q(sex__icontains=search_query) |
            Q(age__icontains=str(search_query)) |
            Q(height__icontains=str(search_query)) |
            Q(weight__icontains=str(search_query)) |
            Q(prediction_result__icontains=search_query)
        )
    else:
        predictions = predictions.all()
    return render(request, 'dashboard.html', {'predictions': predictions})


@login_required
def delete_prediction(request, prediction_id):
    prediction = get_object_or_404(PredictionData, id=prediction_id)
    prediction.delete()
    return redirect('dashboard')

@login_required
def sex_graph_view(request):
    predictions = PredictionData.objects.filter(user=request.user)
    sex_counts = Counter(predictions.values_list('sex', flat=True))
    male_count = sex_counts.get('MALE', 0)
    female_count = sex_counts.get('FEMALE', 0)
    disclaimer = "Disclaimer : This graph is for informational purposes only and may not reflect the actual population distribution."
    context = {
        'male_count': male_count,
        'female_count': female_count,
        'disclaimer': disclaimer,
    }
    return render(request, 'sex_graph.html', context)


@login_required
def nutritional_graph_view(request):
    predictions = PredictionData.objects.filter(user=request.user)
    
    nutritional_counts = Counter(predictions.values_list('prediction_result', flat=True))
    normal_count = nutritional_counts.get('Normal', 0)
    obese_count = nutritional_counts.get('Obese', 0)
    over_weight_count = nutritional_counts.get('Over Weight', 0)
    moderately_wasted_count = nutritional_counts.get('Moderately Wasted', 0)
    severely_wasted_count = nutritional_counts.get('Severely Wasted', 0)
    disclaimer = "Disclaimer : The information presented here is based on predicted nutritional status and may not be entirely accurate. "
    context = {
        'normal_count': normal_count,
        'obese_count': obese_count,
        'over_weight_count': over_weight_count,
        'moderately_wasted_count': moderately_wasted_count,
        'severely_wasted_count': severely_wasted_count,
        'disclaimer': disclaimer,
    }
    return render(request, 'nutritional_graph.html', context)


@login_required
def age_graph_view(request):
    predictions = PredictionData.objects.filter(user=request.user)
    
    age_data = [prediction.age for prediction in predictions]
    nutritional_status_data = [prediction.prediction_result for prediction in predictions]
    disclaimer = "Disclaimer :This information explores the relationship between age and predicted nutritional status."
    context = {
        'age_data': age_data,
        'nutritional_status_data': nutritional_status_data,
        'disclaimer': disclaimer,
    }
    return render(request, 'age_graph.html',context)


@login_required
def height_graph_view(request):
    predictions = PredictionData.objects.filter(user=request.user)
    
    height_data = [prediction.height for prediction in predictions]
    nutritional_status_data = [prediction.prediction_result for prediction in predictions]
    disclaimer = "Disclaimer :This information explores the relationship between height and predicted nutritional status. "
    context = {
        'height_data': height_data,
        'nutritional_status_data': nutritional_status_data,
        'disclaimer': disclaimer,
    }
    return render(request, 'height_graph.html',context)


@login_required
def weight_graph_view(request):
    predictions = PredictionData.objects.filter(user=request.user)
    
    weight_data = [prediction.weight for prediction in predictions]
    nutritional_status_data = [prediction.prediction_result for prediction in predictions]
    disclaimer = "Disclaimer :This information explores the relationship between weight and predicted nutritional status."
    context = {
        'weight_data': weight_data,
        'nutritional_status_data': nutritional_status_data,
        'disclaimer': disclaimer,
    }
    return render(request, 'weight_graph.html',context)



@login_required
def bar_graph_view(request):
    predictions = PredictionData.objects.filter(user=request.user)
    sex_nutritional_counts = predictions.values('sex', 'prediction_result').annotate(count=Count('id'))
    male_counts = {}
    female_counts = {}
    for record in sex_nutritional_counts:
        sex = record['sex']
        nutritional_status = record['prediction_result']
        count = record['count']
        if sex == 'MALE':
            male_counts[nutritional_status] = count
        else:
            female_counts[nutritional_status] = count
    nutritional_status_labels = set(record['prediction_result'] for record in sex_nutritional_counts)
    disclaimer = "Disclaimer : This graph is for informational purposes only and may not reflect the actual population distribution."
    context = {
        'male_counts': male_counts,
        'female_counts': female_counts,
        'nutritional_status_labels': nutritional_status_labels,
        'disclaimer': disclaimer,
    }
    print("Male Counts:", male_counts)
    print("Female Counts:", female_counts)
    print("Nutritional Status Labels:", nutritional_status_labels)
    print("Disclaimer:", disclaimer)
    return render(request, 'bar_graph.html', context)



@login_required
def overtime_view(request):
    predictions = PredictionData.objects.filter(user=request.user)
 
    nutritional_status_data = list(predictions.values_list('prediction_result', flat=True))
    submitted_times = list(predictions.values_list('submitted_time', flat=True))
    
    disclaimer = "Disclaimer: This graph is for informational purposes only and may not reflect the actual population distribution."
    context = {
        'nutritional_status_data': nutritional_status_data,
        'submitted_times': submitted_times,
        'disclaimer': disclaimer,
    }
    return render(request, 'overtime.html', context)


from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
import uuid
def reset_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, 'No user with that username exists.')
            return redirect('reset') 
        token = str(uuid.uuid4())
        reset_link = f"{request.scheme}://{request.get_host()}/password-reset/{token}/"
        send_mail(
            'Password Reset',
            f'Click the link below to reset your password:\n{reset_link}',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        messages.success(request, 'An email with instructions to reset your password has been sent to your email address.')
        return redirect('login')  
    return render(request, 'reset.html')


def change_password_view(request):
        return render(request, 'change_password.html')