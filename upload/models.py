from django.db import models
from PIL import Image
import diplib as dip
import os
import pandas as pd
from io import BytesIO
from django.conf import settings
import cv2
import easyocr
import pandas as pd
from tqdm import tqdm
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer, WordNetLemmatizer
from rapidfuzz import process

import nltk
nltk.download('punkt_tab')
# Initialize NLTK components
nltk.download('stopwords')
nltk.download('punkt')
stemmer = PorterStemmer()
lemmatizer = WordNetLemmatizer()

# Define the function to check for important words
important_words = [
    "Kemmler", "Rohm", "Perspex", "Evonik", "Exolon", "Composites",
    "Arla", "Plast", "greencast", "plexiglas", "deglas", "Crylux",
    "nudec", "PMMA", "PELD", "Crylon", "Makrolon", "Impex HC",
    "Impex", "Markroclear", "PC", "Polycarbonate", "Weiss", "Farblos",
    "Optical", "WH73"
]

# Define the cleaning function
def clean_text(text):
    # Convert bytes-like object to string (assuming UTF-8 encoding)
    text_str = text.decode('utf-8') if isinstance(text, bytes) else text
    
    # Remove special characters, digits, and punctuation
    cleaned_text = re.sub(r'[^a-zA-Z\s]', '', text_str)
    
    # Convert to lowercase
    cleaned_text = cleaned_text.lower()
    
    # Remove extra whitespace
    cleaned_text = ' '.join(cleaned_text.split())
    
    return cleaned_text

# Define the preprocessing function
def preprocess_text(text, use_stemming=True):
    # Tokenize the text
    tokens = word_tokenize(text)
    
    # Remove stop words
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [word for word in tokens if word not in stop_words]
    
    # Apply stemming or lemmatization
    if use_stemming:
        processed_tokens = [stemmer.stem(word) for word in filtered_tokens]
    else:
        processed_tokens = [lemmatizer.lemmatize(word) for word in filtered_tokens]
    
    # Keep only tokens longer than 3 characters
    processed_tokens = [word for word in processed_tokens if len(word) > 3]
    
    # Remove tokens with more than 2 numbers
    processed_tokens = [word for word in processed_tokens if len(re.findall(r'\d', word)) <= 2]
    
    return processed_tokens

    
def check_important_words(text, important_words, threshold=80):
    found_words = []
    text_words = preprocess_text(text)  # Assume this returns a list of words
    for word in important_words:
        word_lower = word.lower()  # Convert each important word to lowercase
        for text_word in text_words:
            text_word_lower = text_word.lower()  # Convert each text word to lowercase
            match = process.extractOne(word_lower, [text_word_lower], score_cutoff=threshold)
            if match:
                found_words.append(word)
                break  # Stop checking this word once a match is found
    return found_words


class UploadedImage(models.Model):
    title = models.CharField(primary_key=True, max_length=100, help_text='Enter an image title')
    image = models.ImageField(upload_to='images/')

    def __str__(self):
        return self.title

    def get_image_dimensions(self):
        """Return the dimensions of the image."""
        with Image.open(self.image) as img:
            return img.size  # (width, height)

    def getname(self):
        """Get the original filename."""
        print( os.path.join(settings.MEDIA_ROOT, self.image.name))
        return self.image.name

    def getferet(self):
        """Calculate Feret diameters, Perimeter, and SolidArea using diplib."""
        
        try:
            # Construct the absolute path to the image
            # Construct the absolute path to the current image
            image_path = self.image.path
            background_image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Main.jpeg')
              # Path to the background image
            
            # Load the background and current image using diplib
            bg = dip.ImageRead(background_image_path) 
            img = dip.ImageRead(image_path)
            
            # Perform operations as before
            diff = dip.MaximumTensorElement(dip.Abs(img - bg))
            diff = dip.MedianFilter(diff)
            
            # Threshold to create binary mask
            objects = diff > 10  # Adjust threshold as needed
            
            # Pick the object in the center of the field of view
            objects = dip.Label(objects)
            label = objects[objects.Size(0) // 2, objects.Size(1) // 2]
            mask = objects == label
            
            # Measure Feret diameters
            msr = dip.MeasurementTool.Measure(+mask, features=['Feret'])
            max_len, min_len, _, _, _ = msr[1]['Feret']  # Only interested in Feret diameters
            
            # Measure Perimeter
            perimeter_msr = dip.MeasurementTool.Measure(+mask, features=['Perimeter'])
            perimeter = perimeter_msr[1]['Perimeter'][0]  # Perimeter value
            
            # Measure SolidArea
            solid_area_msr = dip.MeasurementTool.Measure(+mask, features=['SolidArea'])
            solid_area = solid_area_msr[1]['SolidArea'][0]  # Solid area value

            area_msr = dip.MeasurementTool.Measure(+mask,features=['Size'])
            area = area_msr[1]['Size'][0]  # Solid area value
            # Return the measurements as a dictionary
            return {
                'max_len': max_len *0.04,
                'min_len': min_len*0.04,
                'perimeter': perimeter*0.04,
                'solid_area': solid_area*0.04*0.04,
                'ratio': (area/solid_area) *100,
            }

        except Exception as e:
            print(f"Error processing image {image_path}: {e}")
            return None

            
    def extract_text(self):
        """Extract text from the uploaded image using EasyOCR."""
        try:
            # Initialize EasyOCR reader
            reader = easyocr.Reader(['en'])
            
            # Load the image using OpenCV
            image = cv2.imread(self.image.path)

            # Function to rotate the image
            def rotate_image(image, angle):
                (h, w) = image.shape[:2]
                center = (w / 2, h / 2)
                matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
                rotated = cv2.warpAffine(image, matrix, (w, h))
                return rotated

            # Initialize an empty list to store text results
            results = []

            # Rotate the image by 0, 90, 180, and 270 degrees
            for angle in tqdm(range(0, 360, 90), desc=f"Rotating {self.image.name}"):
                rotated_image = rotate_image(image, angle)

                # Perform OCR using EasyOCR
                result = reader.readtext(rotated_image)

                # Concatenate all detected texts into one string
                concatenated_text = ' '.join([detection[1] for detection in result if len(detection[1]) > 2])

                # Append text result for the current rotation
                results.append({'angle': angle, 'text': concatenated_text})

            # Optionally, combine all results into a single string or further process as needed
            combined_text = ' '.join([entry['text'] for entry in results])


                    # Clean and preprocess the combined text
            cleaned_text = clean_text(combined_text)
            important_words_found = check_important_words(cleaned_text, important_words)

            # Return or process the final cleaned text and important words
            return combined_text,important_words_found

        except Exception as e:
            print(f"Error extracting text from image {self.image.path}: {e}")
            return None,[]

