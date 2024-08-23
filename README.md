# PMMA Sheet Analysis and Classification System

This repository contains a Django project designed for analyzing and classifying PMMA (Polymethyl Methacrylate) sheets. The project leverages both image processing techniques and machine learning models to extract features from images of PMMA sheets and classify the material type. Additionally, it includes a Power BI dashboard to visualize various characteristics of the analyzed items.

## Features

### 1. **Image Feature Extraction**
- **Size and Perimeter:** Automatically calculates the size and perimeter of holes or cutouts in the PMMA sheets.
- **Ratio of Holes:** Computes the ratio of hole areas to the total sheet area.
- **Text Recognition:** Detects and extracts any text present on the PMMA sheets using Optical Character Recognition (OCR) techniques.

### 2. **Hybrid Classification Model**
- **CNN-Based Feature Extraction:** Utilizes Convolutional Neural Networks (CNN) to extract deep features from images, such as texture and surface details.
- **Machine-Detected Features:** Integrates additional information obtained from external sources (such as color, weight, thickness, etc.) for comprehensive material analysis.
- **Material Classification:** Predicts the material type (e.g., PMMA XT, PMMA XG, PC, SUN, PP, PT) based on the combination of image features and machine-detected characteristics.

### 3. **Power BI Dashboard**
- **Visualization:** The project includes a Power BI dashboard that visualizes characteristics of the analyzed items, such as origin, material type, and other extracted features.
- **Insights:** Provides actionable insights based on the analysis, aiding in decision-making processes regarding material handling and usage.

## Project Structure

- **/project_name/**
  - `settings.py`: Django settings and configurations.
  - `urls.py`: URL routing for the project.
  - `models.py`: Database models for storing sheet information and analysis results.
  - `views.py`: Handles requests and responses, including rendering templates and processing image uploads.
  - `admin.py`: Admin interface setup for managing the project data.
  
- **/analysis/**
  - `feature_extraction.py`: Scripts for image processing and feature extraction.
  - `classification.py`: Contains the hybrid model for material classification.
  - `ocr.py`: Text recognition functions.
  - `models/`: Pre-trained CNN models and any additional machine learning models used for classification.

- **/templates/**
  - HTML templates for rendering the web pages.

- **/static/**
  - CSS, JavaScript, and image files for the web interface.

- **/dashboard/**
  - Power BI reports and dashboard files.

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/MohamedDhibi/Sheet-Classification-Django.git
   cd pmma-sheet-analysis
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the Django server:
   ```bash
   python manage.py runserver
   ```

4. Access the application at `http://127.0.0.1:8000/`.

## Usage

- **Uploading Images:** Use the web interface to upload images of PMMA sheets.
- **Feature Extraction:** The system will automatically extract features and perform classification.
- **View Results:** Access the Power BI dashboard to visualize and explore the analysis results.

## Power BI Dashboard

The Power BI dashboard provides a comprehensive view of the analyzed data, including:

- **Material Origin:** Geographic origin of the PMMA sheets.
- **Material Type:** Classification results and distribution of materials.
- **Feature Analysis:** Visual representation of extracted features such as size, color, and weight.

## Future Work

- Improve the accuracy of the CNN model by training on a larger dataset.
- Integrate real-time analysis and monitoring capabilities.
- Expand the classification to include more material types.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.

---
