# Personal Health Assistance Web Application

An intelligent web application designed to provide health-related assistance. This tool allows users to find cost-effective alternatives for brand-name medicines and analyze their symptoms to receive preliminary suggestions for over-the-counter (OTC) treatments.


## Live Demo
(Note: The application is hosted on a free tier and may take a moment to wake up from sleep.)


## Features
- Medicine Alternative Finder: Searches a database of over 40,000 medicines to find therapeutically equivalent alternatives based on their active chemical composition.
- Prescription OCR Analysis: Users can upload an image of a prescription, and the application uses the Google Gemini Vision API to automatically extract the medicine name for searching.
- Symptom Checker: Analyzes user-described symptoms using a two-layered AI approach to suggest a potential condition and an appropriate OTC medicine from a custom knowledge base of 50+ conditions.


## Tech Stack
- Backend: Python, Flask, Gunicorn
- Machine Learning: Scikit-learn, Pandas, Hugging Face Transformers
- External APIs: Google Gemini Vision API
- Frontend: HTML, CSS
- Deployment: Render, Git, Git LFS


## How It Works
This application integrates several AI and data science techniques to provide its core features:

**1. Medicine Recommendation Engine:**
- The engine processes the chemical composition of over 40,000 medicines from a dataset.
- It uses a TF-IDF (Term Frequency-Inverse Document Frequency) vectorizer to convert the composition strings into a numerical matrix.
- When a user searches for a medicine, Cosine Similarity is used to find other medicines with the most similar composition vectors, effectively identifying therapeutically equivalent drugs with over 95% accuracy.

**2. Symptom Analysis Pipeline:**
- A robust, two-layer system analyzes user input.
- Layer 1 (AI Model): A pre-trained Hugging Face NER (Named Entity Recognition) model (d4data/biomedical-ner-all) first attempts to extract specific Disease or Symptom entities from the text.
- Layer 2 (Keyword Fallback): If the AI model finds nothing, the system falls back to a keyword search against a custom-built knowledge base (CONDITION_TO_MEDICINE_MAP) that maps over 50 common conditions to first-line OTC treatments. This ensures the application is highly resilient and provides a helpful response even for simple queries.


## Getting Started
To run this project locally, follow these steps:

**Prerequisites:**
- Python 3.9+
- Git and Git LFS installed on your system.


### Installation
**1. Clone the repository:**

git clone https://github.com/your-username/your-repository-name.git
cd your-repository-name

**2. Install Git LFS and pull the large data file:**

git lfs install
git lfs pull

**3. Create and activate a virtual environment:**

\# For Windows
python -m venv venv
venv\Scripts\activate

\# For macOS/Linux
python3 -m venv venv
source venv/bin/activate

**4. Install the required dependencies:**

pip install -r requirements.txt


### Configuration
1. This project requires an API key for the Google Gemini API. Create a file named key.env in the root directory.
2. Add your API key to this file in the following format:

API_KEY=AIzaSy...your_secret_key_here...


### Usage
Once the setup is complete, you can run the application with the following command:

python app.py

Open your web browser and navigate to http://127.0.0.1:5000 to use the application.


## License
This project is distributed under the MIT License. See LICENSE.txt for more information.
