from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification

model_name = "d4data/biomedical-ner-all"



try:
    print("Loading biomedical NER model...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForTokenClassification.from_pretrained(model_name)
    
    symptom_extractor = pipeline(
        "ner", model=model, tokenizer=tokenizer, aggregation_strategy="simple"
    )
    print("Model loaded successfully.")
except Exception as e:
    print(f"Error loading NER model: {e}")
    symptom_extractor = None




def get_condition_from_symptoms(symptoms_text):

    """
    Analyzes symptoms using only the advanced AI NER model.
    It will return an empty list if no specific medical entities are found.
    """

    if not symptom_extractor or not symptoms_text:
        return []

    try:
        entities = symptom_extractor(symptoms_text)
        diseases = [
            {'name': entity['word'].capitalize(), 'probability': entity['score'] * 100}
            for entity in entities if entity['entity_group'] == 'Disease'
        ]
        if diseases:
            return diseases
        
        # Fallback to finding a 'Symptom' if no 'Disease' is found
        symptoms = [
            {'name': entity['word'].capitalize(), 'probability': entity['score'] * 100}
            for entity in entities if entity['entity_group'] == 'Symptom'
        ]
        return symptoms
        
    except Exception as e:
        print(f"An error occurred during NER prediction: {e}")
        return []
