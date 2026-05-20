import os
import json
import re
from bs4 import BeautifulSoup

dossier_html = "sources"
fichier_sortie = "./database.json"
base_de_donnees = []

# Liste tous les fichiers HTML du dossier
fichiers_html = [f for f in os.listdir(dossier_html) if f.endswith('.html')]

def a_le_style_rouge(tag):
    """Vérifie si la balise ELLE-MÊME a une couleur rouge ou la classe correct_answer"""
    if not tag or not hasattr(tag, 'get'):
        return False
    
    classes = tag.get('class', [])
    if isinstance(classes, list) and 'correct_answer' in classes:
        return True
    if isinstance(classes, str) and 'correct_answer' in classes.split():
        return True
        
    style = tag.get('style', '').lower()
    # On couvre les standards de itexamanswers
    if 'red' in style or '#ff0000' in style:
        return True
    return False

def contient_reponse_rouge(tag):
    """Vérifie si la balise ou l'un de ses ENFANTS directs a le style rouge"""
    if a_le_style_rouge(tag):
        return True
    for child in tag.find_all(True):
        if a_le_style_rouge(child):
            return True
    return False

for nom_fichier in fichiers_html:
    chemin_fichier = os.path.join(dossier_html, nom_fichier)
    print(f"Analyse de {nom_fichier}...")
    
    with open(chemin_fichier, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')
        
        # Trouver toutes les questions (qu'elles soient en <strong> ou <b>)
        questions_elements = soup.find_all(['strong', 'b'])
        blocs_traites = set()
        
        for q_el in questions_elements:
            question_texte = q_el.get_text(strip=True)
            if len(question_texte) < 5:
                continue
                
            # SÉCURITÉ : Sommes-nous DANS une réponse ?
            # On remonte les parents pour voir si on est dans un <li> ou un bloc rouge
            parent = q_el
            is_answer = False
            while parent and parent.name not in ['body', 'html']:
                if parent.name in ['li', 'ul', 'ol']:
                    is_answer = True
                    break
                # On vérifie uniquement l'élément lui-même, pas tout son contenu !
                if a_le_style_rouge(parent):
                    is_answer = True
                    break
                parent = parent.parent
                
            if is_answer:
                continue
                
            # On cible le paragraphe entier de la question
            bloc_courant = q_el.find_parent(['p', 'div', 'h2', 'h3'])
            if not bloc_courant:
                bloc_courant = q_el
                
            # Empêche de doubler l'extraction si deux mots sont en gras dans la même question
            if id(bloc_courant) in blocs_traites:
                continue
            blocs_traites.add(id(bloc_courant))
                
            full_question_texte = bloc_courant.get_text(separator=' ', strip=True)
            
            reponses = []
            explication = ""
            
            voisin = bloc_courant.find_next_sibling()
            
            # On va scanner les 30 éléments maximum sous la question
            for _ in range(30):
                if not voisin:
                    break
                
                # CONDITION D'ARRÊT : Si on tombe sur la question suivante
                if voisin.name in ['p', 'div', 'h2', 'h3']:
                    has_strong = voisin.find(['strong', 'b'])
                    text_voisin = voisin.get_text(strip=True)
                    # Si c'est en gras, que ce n'est pas une réponse, et que ça commence par un chiffre (ex: "42. ")
                    if has_strong and not contient_reponse_rouge(voisin) and re.match(r'^\s*\d+[\.\)]', text_voisin):
                        break
                
                # 1. Extraction dans les listes QCM (<ul> / <ol>)
                if voisin.name in ['ul', 'ol']:
                    for li in voisin.find_all('li'):
                        if contient_reponse_rouge(li):
                            reponses.append(li.get_text(separator=' ', strip=True))
                            
                # 2. Extraction hors listes (texte libre rouge)
                elif contient_reponse_rouge(voisin):
                    rouges = []
                    if a_le_style_rouge(voisin):
                        rouges.append(voisin)
                    else:
                        for child in voisin.find_all(True):
                            if a_le_style_rouge(child):
                                rouges.append(child)
                                
                    for r in rouges:
                        txt = r.get_text(separator=' ', strip=True)
                        if txt and txt not in reponses:
                            reponses.append(txt)
                        
                # 3. Explication (boîtes de message sur les sites)
                classes = voisin.get('class', []) if hasattr(voisin, 'get') else []
                if isinstance(classes, list) and ('message_box' in classes or 'announce' in classes or 'success' in classes):
                    explication = voisin.get_text(separator='\n', strip=True)
                    
                voisin = voisin.find_next_sibling()
                
            # On ajoute à la DB uniquement si on a récupéré une réponse ou une explication
            if reponses or explication:
                reponses = list(dict.fromkeys(reponses)) # Enlève les doublons stricts
                base_de_donnees.append({
                    "question": full_question_texte,
                    "reponses": reponses,
                    "explication": explication,
                    "source": nom_fichier
                })

# Sauvegarde finale
with open(fichier_sortie, 'w', encoding='utf-8') as f:
    json.dump(base_de_donnees, f, ensure_ascii=False, indent=4)

print(f"\n✅ SUCCESS ! {len(base_de_donnees)} questions extraites dans {fichier_sortie}")
