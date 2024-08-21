# views.py
from django.http import HttpResponse 
from django.shortcuts import render, redirect 
from upload.models import UploadedImage
from .forms import *
import os
from django.conf import settings
import openai
# Configure OpenAI API key
def home(request):
    return render(request, 'home.html')


def index(request):
    alert_message = None
    recent_image = None
    measurements = None
    Detected_Words= None
    extracted_text = None  # Initialize extracted_text with a default value
    if request.method == 'POST':
        submitted_form = UploadImageForm(request.POST, request.FILES)

        if submitted_form.is_valid():
            uploaded_file = request.FILES['image']
            file_name_without_extension = os.path.splitext(uploaded_file.name)[0]

            if UploadedImage.objects.filter(title=file_name_without_extension).exists():
                alert_message = {
                    'status': False,
                    'message': f'A file with the title "{file_name_without_extension}" already exists. Please rename your file and try again.'
                }
            else:
                uploaded_image = submitted_form.save(commit=False)
                uploaded_image.title = file_name_without_extension
                uploaded_image.save()

                # Calculate measurements and store them in the text file
                measurements = uploaded_image.getferet()
                
                # Save measurements to a text file
                measurements_file_path = os.path.join('media', 'measurements.txt')
                with open(measurements_file_path, 'a') as f:
                    f.write(f"Title: {file_name_without_extension}\n")
                    f.write(f"Max Feret Diameter: {measurements['max_len']}\n")
                    f.write(f"Min Feret Diameter: {measurements['min_len']}\n")
                    f.write(f"Perimeter: {measurements['perimeter']}\n")
                    f.write(f"Solid Area: {measurements['solid_area']}\n")
                    f.write(f"Ratio: {measurements['ratio']}\n")
                    f.write("-" * 40 + "\n")

                # Store the primary key of the recently uploaded image in the session
                request.session['recent_image_id'] = uploaded_image.pk

                return redirect('index')
            
    
    if request.method == 'GET':
        recent_image_id = request.session.pop('recent_image_id', None)
        if recent_image_id:
            recent_image = UploadedImage.objects.filter(pk=recent_image_id).first()
            if recent_image:
                # Calculate measurements dynamically for display
                measurements = recent_image.getferet()

                # Extract text for display
                extracted_text,Detected_Words = recent_image.extract_text()
        
                    # Round the measurements to two decimal places
                measurements['max_len'] = round(measurements['max_len'], 2)
                measurements['min_len'] = round(measurements['min_len'], 2)
                measurements['perimeter'] = round(measurements['perimeter'], 2)
                measurements['solid_area'] = round(measurements['solid_area'], 2)
                measurements['ratio'] = round(measurements['ratio'], 2)

    context = {
        'alert_data': alert_message,
        'recent_image': recent_image,
        'measurements': measurements,
        'extracted_text': extracted_text,
        'Detected_Words':Detected_Words,  # Add extracted text to context
    }
    return render(request, 'index.html', context=context)
