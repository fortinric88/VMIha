# VMI Ventilairsec for Home Assistant

Cette intégration custom Home Assistant est une adaptation du backup Jeedom fourni dans les dossiers openenocean et ventilairsec.

## Fonctionnalités
- Lecture des capteurs EnOcean supportés : A5-09-04, A5-04-01, D1079-00-00, D1079-01-00
- Décodage des messages VMI Ventilairsec à partir du format proprietary D1079
- Prise en charge de la liaison série sur /dev/ttyS2
- Entités de base : capteurs, select et number

## Installation
1. Copier le dossier custom_components/vmi_ventilairsec dans votre installation Home Assistant.
2. Redémarrer Home Assistant.
3. Ajouter l’intégration via l’interface.

## Notes
Le parser de payloads est basé sur les définitions XML présentes dans le backup Jeedom et doit être complété avec un vrai transport série si vous souhaitez piloter les unités VMI en temps réel.
