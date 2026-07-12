Debug logger pour l'intégration `vmi_ventilairsec`

But: copiez le contenu de `logger_vmi_ventilairsec.yaml` dans la configuration de Home Assistant pour activer le niveau DEBUG pour cette intégration.

Options d'installation :

1) Ajouter directement dans `configuration.yaml` :

logger:
  default: info
  logs:
    custom_components.vmi_ventilairsec: debug
    custom_components.vmi_ventilairsec.enocean_listener: debug
    custom_components.vmi_ventilairsec.enocean_handler: debug

2) Ou inclure le fichier fourni (préféré si vous souhaitez garder la configuration organisée) :

Dans `configuration.yaml` ajoutez :

logger: !include debug/logger_vmi_ventilairsec.yaml

Puis redémarrez Home Assistant. Les logs détaillés apparaîtront dans `Settings → System → Logs` ou dans vos fichiers de log selon votre installation.

Remarque : pensez à remettre le niveau `debug` à `info` ou supprimer ces lignes après le débogage pour éviter un log verbeux permanent.