# **C.I.P.H.E.R-hearing**
Programme de reconnaissance vocale compatible avec le logiciel de robotique C.I.P.H.E.R. Il se présente sous la forme d'une application exécutée en local. Le coeur de la reconnaissance se base sur 3 composantes:
- [Rhasspy Raven](https://github.com/rhasspy/rhasspy-wake-raven), un détecteur de wakework pouvant être entrainé localement.
- [Vosk](https://alphacephei.com/vosk/), un moteur de transcription vocal basé sur Kaldi.
- [Snips NLU](https://github.com/snipsco/snips-nlu), une bibliothèque Python de compréhension du langage.

La processus ce déroule d'une façon similaire à n'importe quel système de reconnaissance vocale:
- Détection du mot clé d'activaton.
- Ecoute et transcription sous forme de texte.
- Analyse du texte et reconnaissance des intentions.
- Envoie du résultat au serveur via MQTT. 