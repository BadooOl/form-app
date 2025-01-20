from flask import Flask, request, render_template_string, jsonify
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import os
from datetime import datetime

app = Flask(__name__)

# Debug mode flag
DEBUG_MODE = False  # Just change this to False when you want to test with real validation

def get_debug_values():
    if not DEBUG_MODE:
        return {}
    
    return {
        'prenom': 'John',
        'nom': 'Doe',
        'dob': '1990-01-01',
        'email': 'john.doe@example.com',
        'phone': '0123456789',
        'operation': 'non',
        'operationDetails': '',
        'antecedents': ['aucun'],
        'allergies': 'non',
        'allergiesDetails': '',
        'enceinte': 'non',
        'semainesGrossesse': '',
        'sommeil': '3',
        'massage': 'surmesure',
        'relaxant': '30',
        'antiAge': '30',
        'detente': '40'
    }

@app.route('/', methods=['GET'])
def home():
    return render_template_string(open('index.html').read())

@app.route('/form', methods=['POST'])
def handle_form():
    # Log des données reçues
    print("Données reçues :", request.form)

    # Merge debug values with form data if in debug mode
    form_data = request.form.copy()
    if DEBUG_MODE:
        debug_values = get_debug_values()
        for key, value in debug_values.items():
            if not form_data.get(key):
                form_data[key] = value

    # Champs requis
    required_fields = [
        'prenom', 'nom', 'dob', 'email', 'phone',
        'operation', 'allergies', 'enceinte'
    ]

    # Skip validation in debug mode
    if not DEBUG_MODE:
        missing_fields = [field for field in required_fields if not form_data.get(field)]
        if missing_fields:
            return jsonify({
                "error": "Certains champs requis sont manquants",
                "missing_fields": missing_fields
            }), 400

    # Création du PDF
    pdf_dir = "pdfs"
    os.makedirs(pdf_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf_path = os.path.join(pdf_dir, f"massage_{form_data['nom']}_{timestamp}.pdf")

    c = canvas.Canvas(pdf_path, pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(1*inch, 10*inch, "Formulaire de Massage")
    
    # Position de départ pour le contenu
    y_position = 9*inch
    line_height = 0.25*inch
    
    def add_section_title(title):
        nonlocal y_position
        y_position -= line_height
        c.setFont("Helvetica-Bold", 12)
        c.drawString(1*inch, y_position, title)
        y_position -= line_height
        c.setFont("Helvetica", 10)

    def add_field(label, value):
        nonlocal y_position
        c.drawString(1*inch, y_position, f"{label}: {value}")
        y_position -= line_height

    # Informations personnelles
    add_section_title("Informations Personnelles")
    add_field("Prénom", form_data.get('prenom'))
    add_field("Nom", form_data.get('nom'))
    add_field("Date de naissance", form_data.get('dob'))
    add_field("Email", form_data.get('email'))
    add_field("Téléphone", form_data.get('phone'))

    # Opération chirurgicale
    add_section_title("Opération Chirurgicale")
    operation = form_data.get('operation')
    details = form_data.get('operationDetails', '')
    add_field("Opération récente", "Oui" if operation == "oui" else "Non")
    if operation == "oui" and details:
        add_field("Détails", details)

    # Antécédents médicaux
    add_section_title("Antécédents Médicaux")
    antecedents = request.form.getlist('antecedents')
    if antecedents:
        add_field("Antécédents", ", ".join(antecedents))
    else:
        add_field("Antécédents", "Aucun")

    # Allergies
    add_section_title("Allergies")
    allergies = form_data.get('allergies')
    details = form_data.get('allergiesDetails', '')
    add_field("Présence d'allergies", "Oui" if allergies == "oui" else "Non")
    if allergies == "oui" and details:
        add_field("Détails", details)

    # Grossesse
    add_section_title("Grossesse")
    enceinte = form_data.get('enceinte')
    semaines = form_data.get('semainesGrossesse', '')
    add_field("Enceinte", "Oui" if enceinte == "oui" else "Non")
    if enceinte == "oui" and semaines:
        add_field("Semaines de grossesse", semaines)

    # Qualité du sommeil
    add_section_title("Qualité du Sommeil")
    sommeil = form_data.get('sommeil', 'Non évalué')
    add_field("Évaluation", f"{sommeil}/5" if sommeil != 'Non évalué' else sommeil)

    # Type de massage
    add_section_title("Choix du Massage")
    massage_type = form_data.get('massage')
    add_field("Type de massage choisi", massage_type)

    # Si massage sur mesure, ajouter les pourcentages
    if massage_type == "surmesure":
        add_field("Relaxant", f"{form_data.get('relaxant', '0')}%")
        add_field("Effet anti-âge", f"{form_data.get('antiAge', '0')}%")
        add_field("Détente profonde", f"{form_data.get('detente', '0')}%")

    # Ajouter la date de génération
    y_position = 1*inch
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(1*inch, y_position, f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}")

    c.save()

    return jsonify({
        "message": "PDF généré avec succès",
        "pdf_path": pdf_path
    })

if __name__ == "__main__":
    app.run(debug=True)