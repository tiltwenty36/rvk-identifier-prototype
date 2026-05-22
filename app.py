import os
import sys
from typing import Optional
from pydantic import BaseModel, Field
from openai import OpenAI

# 1. Définition de la structure de données attendue
class RvkClassification(BaseModel):
    rvk_code: str = Field(description="Le code RVK exact (ex: ST 250, AN 73000)")
    category_name: str = Field(description="Le nom de la catégorie en allemand ou en français")
    confidence_score: float = Field(description="Score de confiance entre 0.0 et 1.0")
    justification: str = Field(description="Courte explication du choix de cette classification")

def get_rvk_code(book_title: str) -> Optional[RvkClassification]:
    """
    Analyse le titre d'un livre et suggère un code RVK en utilisant un LLM.
    """
    # Vérification de la clé API
    if not os.environ.get("OPENAI_API_KEY"):
        print("Erreur : La variable d'environnement OPENAI_API_KEY n'est pas configurée.")
        sys.exit(1)
        
    client = OpenAI()

    prompt = f"""
    Tu es un expert en bibliothéconomie spécialisé dans la classification RVK (Regensburger Verbundklassifikation).
    Analyse le titre du livre suivant et détermine son code RVK le plus probable, la catégorie correspondante, et ton score de certitude.
    
    Titre du livre : "{book_title}"
    
    Règles strictes :
    1. Le code RVK doit respecter la syntaxe standard (ex: Deux lettres suivies de chiffres, comme 'ST 250').
    2. Si le titre est en français, traduis mentalement le concept pour trouver la correspondance exacte dans la notation RVK (qui est initialement en allemand).
    """

    try:
        completion = client.beta.chat.completions.parse(
            model="gpt-4o-mini",  # Idéal, rapide et économique pour ce prototype
            messages=[
                {"role": "system", "content": "Tu es un outil d'automatisation de catalogage de bibliothèque."},
                {"role": "user", "content": prompt}
            ],
            response_format=RvkClassification,
        )
        return completion.choices[0].message.parsed
    except Exception as e:
        print(f"Une erreur est survenue lors de l'appel à l'API : {e}")
        return None

if __name__ == "__main__":
    print("--- Prototype de Suggestion de Code RVK ---")
    if len(sys.argv) > 1:
        title = " ".join(sys.argv[1:])
    else:
        title = input("Entrez le titre du livre : ")

    if not title.strip():
        print("Le titre ne peut pas être vide.")
        sys.exit(0)

    print(f"\nAnalyse de : '{title}'...")
    result = get_rvk_code(title)

    if result:
        print("\n" + "="*40)
        print(f"Code RVK Proposé :  {result.rvk_code}")
        print(f"Catégorie :         {result.category_name}")
        print(f"Confiance :         {result.confidence_score * 100:.1f}%")
        print(f"Justification :     {result.justification}")
        print("="*40)
