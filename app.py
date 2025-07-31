from flask import Flask, render_template, request, redirect, url_for, flash
import os
import symptom_analyzer
from image_to_text_checkpoint import image_to_text
import similarity_search_checkpoint as similarity_search

app = Flask(__name__)

app.secret_key = 'a-truly-random-secret-key-for-production'

# "Knowledge Base" to Map Conditions to Recommended Medicines
CONDITION_TO_MEDICINE_MAP = {
    # Common Ailments
    "Fever": "Paracetamol",
    "Headache": "Ibuprofen",
    "Common Cold": "Cetirizine",
    "Cough": "Dextromethorphan",
    "Body Ache": "Paracetamol",
    "Sore Throat": "Lozenges",
    "Migraine": "Naproxen",
    "Allergy": "Loratadine",
    "Nasal Congestion": "Pseudoephedrine",
    "Runny Nose": "Chlorpheniramine",
    
    # Digestive Issues
    "Stomach Ache": "Antacid",
    "Diarrhea": "Loperamide",
    "Constipation": "Bisacodyl",
    "Indigestion": "Simethicone",
    "Acid Reflux": "Omeprazole",
    "Nausea": "Dimenhydrinate",
    "Vomiting": "Ondansetron",
    "Gas": "Simethicone",
    "Heartburn": "Ranitidine",
    
    # Skin Conditions
    "Acne": "Benzoyl Peroxide",
    "Eczema": "Hydrocortisone Cream",
    "Psoriasis": "Salicylic Acid",
    "Fungal Infection": "Clotrimazole",
    "Rash": "Calamine Lotion",
    "Sunburn": "Aloe Vera",
    "Dandruff": "Ketoconazole Shampoo",
    "Insect Bite": "Diphenhydramine Cream",

    # Pain & Inflammation
    "Muscle Pain": "Diclofenac",
    "Joint Pain": "Naproxen",
    "Arthritis": "Glucosamine",
    "Back Pain": "Aceclofenac",
    "Menstrual Cramps": "Mefenamic Acid",
    
    # More Critical/Specific Conditions
    "Influenza": "Oseltamivir",
    "Hypertension": "Amlodipine",
    "Diabetes": "Metformin",
    "Asthma": "Salbutamol Inhaler",
    "Anxiety": "Alprazolam",
    "Depression": "Sertraline",
    "Insomnia": "Melatonin",
    "High Cholesterol": "Atorvastatin",
    "Urinary Tract Infection": "Nitrofurantoin",
    "Anemia": "Ferrous Sulfate",
    "Osteoporosis": "Calcium Carbonate",
    "Gout": "Allopurinol",
    "Thyroid issue": "Levothyroxine",
    
    # Infections
    "Bacterial Infection": "Amoxicillin",
    "Ear Infection": "Ciprofloxacin Ear Drops",
    "Eye Infection": "Moxifloxacin Eye Drops",
}




# Home Page Route
@app.route('/')
def index():
    return render_template('index.html')




# F1: Medicine Search (from OCR or Manual Text) with Error Handling
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # Handle manual text search first
        if 'medicine' in request.form and request.form['medicine'].strip() != '':
            medicine_name_from_form = request.form['medicine'].strip()
            return redirect(url_for('search_result', medicine=medicine_name_from_form))

        # Handle file upload
        if 'prescription_image' in request.files and request.files['prescription_image'].filename != '':
            f = request.files['prescription_image']
            upload_folder = os.path.join('static', 'uploads')
            os.makedirs(upload_folder, exist_ok=True)
            input_path = os.path.join(upload_folder, f.filename)
            f.save(input_path)
            
            # Get the result from the OCR function
            medicine_name_from_ocr = image_to_text(input_path)
            
            # Check if the OCR was successful before redirecting
            if medicine_name_from_ocr:
                return redirect(url_for('search_result', medicine=medicine_name_from_ocr))
            else:
                # If OCR failed, flash an error message and stay on the search page
                flash("Could not analyze the image. It might be unclear or an API error occurred. Please try again or search manually.", "error")
                return redirect(url_for('upload'))
                
    # For GET requests, render the search/upload form
    return render_template('search.html')



# Search Result
@app.route('/search-result')
def search_result():
    medicine = request.args.get('medicine', '')
    
    match, comp, alternatives_data, manu, price = similarity_search.search_medicine(medicine)

    main_medicine = {
        "name": match,
        "composition": comp,
        "manufacturer": manu,
        "price": price
    }
    
    alternative_medicines = alternatives_data if alternatives_data else []

    return render_template('results.html',
                           main_medicine=main_medicine,
                           alternative_medicines=alternative_medicines)




# F2: Symptom Checker
@app.route('/symptom', methods=['GET'])
def symptom_input():
    return render_template('symptom_input.html')

@app.route('/symptom-check', methods=['POST'])
def symptom_check():
    symptoms_text = request.form['symptoms']
    
    conditions = symptom_analyzer.get_condition_from_symptoms(symptoms_text)

    if not conditions and symptoms_text:
        for condition_keyword in CONDITION_TO_MEDICINE_MAP.keys():
            if condition_keyword.lower() in symptoms_text.lower():
                conditions = [{'name': condition_keyword, 'probability': 95.0}]
                break

    recommended_medicine = None
    alternative_medicines = []
    
    if conditions:
        top_condition_name = conditions[0]['name']
        medicine_to_search = CONDITION_TO_MEDICINE_MAP.get(top_condition_name, top_condition_name)
        
        match, comp, alternatives_data, manu, price = similarity_search.search_medicine(medicine_to_search)
        
        if match:
            recommended_medicine = {
                "name": match,
                "composition": comp,
                "manufacturer": manu,
                "price": price
            }
            
            if alternatives_data:
                alternative_medicines = alternatives_data

    return render_template('symptom_results.html',
                           conditions=conditions,
                           recommended_medicine=recommended_medicine,
                           alternative_medicines=alternative_medicines)

# Flask App
if __name__ == '__main__':
    app.run(debug=True)
