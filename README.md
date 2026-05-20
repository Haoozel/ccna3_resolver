# CCNA2/3 RESPONDER

Extension chrome permettant d'afficher les réponses des questions directement dans le navigateur.

Fonctionne avec la V7 du CCNA3 et CCNA2. 

Supporte les versions Française et Anglaise du CCNA3, le parsing de la version française est tout pété il vaut mieux l'utiliser en anglais. 
Uniquement la version anglaise pour le CCNA2.

> [!CAUTION]
> Certaines questions sont manquantes dans la version française -> fortement conseillé d'utiliser la version anglaise.

## Structure du projet 
```
.
├── manifest.json         # Configuration de l'extension
├── background.js        # Logique de recherche et gestion des raccourcis
└── database/           # Dossier contenant vos fichiers .html et le .json final
  └── database.json    # Fichier contenant les questions/réponses
```

## Installation

### Prérequis

La plateforme cisco contenant une fonctionnalité de DRM empêchant de copier/coller sur les quizzs de base, une seconde extension activant le copy/paste sera nécessaire à côté de l'extension présentée cisco

exemple d'extension avec laquelle ça fonctionne : 
```
https://chromewebstore.google.com/detail/enable-copy-paste-ecp/fpjppnhnpnknbenelmbnidjbolhandnf
```

### Installation de l'extension custom

> [!IMPORTANT]  
> L'extension ne fonctionne qu'avec les bases chromium

Dans chrome, se rendre sur la page `chrome://extensions`

Activer le mode développeur en haut à droite

Puis ajouter l'extension en cliquant sur "Load unpacked" et charger le dossier (ou fichier manifest.json) de l'extension custom.


## Exécution 

Une fois les 2 extensions requises installées, recharger la page Netacad, puis sélectionner la question et 2 options possibles : 
- Soit faire clic droit et cliquer sur "Chercher la réponse pour: xxx"
- Soit faire la macro Ctrl + Shift + S pour exécuter l'extension directement



