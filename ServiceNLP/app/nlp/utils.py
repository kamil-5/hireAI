import spacy
from PyPDF2 import PdfReader
import fitz  # PyMuPDF
import re

# Charger le modèle spaCy
nlp = spacy.load("en_core_web_sm")


def extract_text_with_pymupdf(file_path):
    """
    Extraire le texte d'un PDF avec PyMuPDF.
    """
    try:
        doc = fitz.open(file_path)
        content = ""
        for page in doc:
            content += page.get_text("text") + "\n"
        return content.strip()
    except Exception as e:
        print(f"Erreur avec PyMuPDF : {e}")
        return ""

def extract_skills_from_chunks(content):
    """
    Extraire des compétences à partir des sections pertinentes d'un texte extrait.
    """
    # Diviser le contenu en lignes
    lines = content.split("\n")
    lines = [line.strip().lower() for line in lines if line.strip()]  # Nettoyer les lignes

    # Mots-clés pour détecter la section compétences
    keywords = ["compétences", "skills", "expertise", "abilities"]

    # Parcourir les lignes pour trouver les mots-clés
    for idx, line in enumerate(lines):
        if any(keyword in line for keyword in keywords):
            # Extraire les lignes suivantes comme compétences jusqu'à un saut de section
            skills = []
            for subsequent_line in lines[idx + 1:]:
                if subsequent_line and not any(keyword in subsequent_line for keyword in keywords):
                    skills.extend(re.split(r"[,\n;]", subsequent_line))  # Séparer par des délimiteurs classiques
                else:
                    break
            # Nettoyer les compétences extraites
            cleaned_skills = [skill.strip().capitalize() for skill in skills if skill.strip()]
            return cleaned_skills if cleaned_skills else ["Aucune compétence détectée"]

    return ["Aucune section 'Compétences' détectée dans le CV."]

def analyze_cv_with_chunks(file_path):
    """
    Analyse un CV et détecte les compétences à partir de la section correspondante.
    
    Args:
        file_path (str): Chemin du fichier PDF.
    
    Returns:
        dict: Résultat contenant un message et les compétences détectées.
    """
    content = extract_text_with_pymupdf(file_path)
    if not content:
        return {"message": "Erreur : Impossible d'extraire le texte du PDF.", "skills": []}

    skills = extract_skills_from_chunks(content)
    return {"message": "Analyse réussie", "skills": skills}

















def extract_skills_from_offers(data, chunk_size=50):
    """
    Extraire les compétences des descriptions d'offres en traitant par chunks et inclure les noms des entreprises.

    Args:
        data (list of dict): Liste de dictionnaires contenant les entreprises et leurs descriptions d'offres.
        chunk_size (int): Taille des chunks en nombre de mots.

    Returns:
        list of dict: Liste contenant les noms des entreprises et leurs compétences détectées.
    """
    try:
        # Liste complète de compétences prédéfinies
        skills_keywords = [
            "python", "django", "sql", "powerbi", "tableau", "aws", "docker",
            "kubernetes", "react", "javascript", "css", "java", "uml", "microservices",
            "agile", "scrum", "jira", "firewall", "siem", "iso27001", "tensorflow",
            "pytorch", "scikit-learn", "node.js", "mongodb", "linux", "bash", "vmware",
            "cybersecurity", "machine learning", "flutter", "kotlin", "swift",
            "azure", "cloud", "itil", "spark", "hadoop", "spring", "hibernate", "figma",
            "sketch", "adobe xd", "excel", "c++", "jenkins", "express", "nlp", "soc2",
            "cisco", "vpn", "tcp/ip", "oracle", "gcp", "html", "graphql", "selenium",
            "cypress", "owasp", "solidity", "ethereum", "confluence", "uipath",
            "automation anywhere", "ruby", "rails", "gitlab ci", "rasa", "kafka",
            "airflow", "iot", "mqtt", "edge computing", "c#", ".net core", "sql server",
            "terraform", "ansible", "testng", "angular", "typescript", "wireshark",
            "rest", "graphql", "jenkins", "security", "api testing"
        ]

        results = []

        for offer in data:
            company = offer.get("company", "Entreprise inconnue")
            description = offer.get("description", "")

            if not description:
                results.append({"company": company, "skills": ["Aucune compétence détectée"]})
                continue

            # Normalisation et nettoyage
            normalized_description = description.lower()

            # Diviser la description en chunks de taille définie
            words = normalized_description.split()
            chunks = [
                " ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)
            ]

            detected_skills = set()

            # Traiter chaque chunk individuellement
            for chunk in chunks:
                # Analyser le chunk avec spaCy
                doc = nlp(chunk)

                # Extraire les entités détectées par spaCy
                extracted_entities = [
                    ent.text.lower() for ent in doc.ents if ent.label_ in ["ORG", "PRODUCT", "SKILL"]
                ]

                # Détecter les mots-clés dans le chunk
                skills_in_chunk = [skill for skill in skills_keywords if skill in chunk]

                # Ajouter les compétences détectées au set
                detected_skills.update(extracted_entities + skills_in_chunk)

            # Logique pour filtrer "r" hors contexte ou compétences invalides
            filtered_skills = [
                skill for skill in detected_skills if skill != "r" or "python" in detected_skills or "machine learning" in detected_skills
            ]

            # Ajouter les résultats
            results.append({"company": company, "skills": sorted(filtered_skills) if filtered_skills else ["Aucune compétence détectée"]})

        return results
    except Exception as e:
        print(f"Erreur lors de l'analyse : {e}")
        return [{"company": "Erreur", "skills": ["Erreur d'analyse"]}]





