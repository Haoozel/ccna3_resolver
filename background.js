// --- GESTION DU CLIC DROIT ---
chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "chercher-reponse",
    title: "Chercher la réponse pour : '%s'", 
    contexts: ["selection"]
  });
});

chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === "chercher-reponse") {
    lancerRecherche(tab.id, info.selectionText);
  }
});

// --- GESTION DU RACCOURCI CLAVIER ---
chrome.commands.onCommand.addListener((command) => {
  if (command === "chercher-reponse-raccourci") {
    chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
      if (tabs[0]) {
        chrome.scripting.executeScript({
          target: { tabId: tabs[0].id, allFrames: true },
          func: () => window.getSelection().toString().trim()
        }, (results) => {
            let texteSurligne = "";
            if (results) {
                for (let res of results) {
                    if (res.result) { texteSurligne = res.result; break; }
                }
            }

            if (texteSurligne) {
                lancerRecherche(tabs[0].id, texteSurligne);
            } else {
                chrome.scripting.executeScript({
                    target: { tabId: tabs[0].id },
                    func: () => alert("❌ Veuillez d'abord surligner une question !")
                });
            }
        });
      }
    });
  }
});

// --- LANCEMENT DE LA RECHERCHE ---
function lancerRecherche(tabId, texteFourni) {
    chrome.scripting.executeScript({
      target: { tabId: tabId },
      func: chercherDansLeJSON,
      args: [texteFourni]
    });
}

// --- LA NOUVELLE FONCTION DE RECHERCHE DANS LE JSON ---
async function chercherDansLeJSON(questionSelectionnee) {
    if (!questionSelectionnee) return;

    try {
        // 1. On charge la base de données JSON unique
        const urlDB = chrome.runtime.getURL('database/database.json');
        const response = await fetch(urlDB);
        const data = await response.json();

        // 2. On cherche la question (insensible à la casse)
        const qCible = questionSelectionnee.toLowerCase().trim();
        
        // On cherche le premier objet du JSON dont la question contient le texte surligné
        const resultat = data.find(item => item.question.toLowerCase().includes(qCible));

        // 3. Affichage du résultat
        if (resultat) {
            let message = `📄 Source : ${resultat.source}\n\n`;
            message += `❓ QUESTION :\n${resultat.question}\n\n`;
            
            if (resultat.reponses && resultat.reponses.length > 0) {
                message += `👉 RÉPONSE(S) :\n✅ ${resultat.reponses.join('\n✅ ')}\n`;
            } else if (resultat.explication) {
                message += `👉 EXPLICATION :\n${resultat.explication}\n`;
            } else {
                message += `⚠️ Format particulier. Vérifiez le fichier JSON.\n`;
            }

            alert(message);
        } else {
            alert(`❌ Question introuvable dans la base JSON.\n\nTexte cherché : "${questionSelectionnee}"`);
        }

    } catch (error) {
        alert("❌ Erreur : Impossible de charger database.json. Avez-vous bien généré le fichier avec Python ?");
        console.error(error);
    }
}
