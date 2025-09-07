# ha-solax-installateur-settings

Intégration personnalisée pour Home Assistant permettant de gérer les paramètres installateur des onduleurs SolaX via l’API HTTP locale. Elle permet de modifier les paramètres installateur sans quitter Home Assistant.

## Prérequis

- Une installation fonctionnelle de Home Assistant
- L’accès au réseau local de l’onduleur
- Le mot de passe installateur de l’onduleur

## Installation

### Via HACS

1. Dans HACS, ajoute le **Référentiel personnalisé** `https://github.com/404GamerNotFound/ha-solax-installateur-settings` de type *Integration*.
2. Après l’ajout, recherche `Solax Installer Settings` dans HACS et installe-le.
3. Redémarre Home Assistant.

### Installation manuelle

1. Copie le répertoire `custom_components/solax_installateur_settings` dans le répertoire `custom_components` de ton installation Home Assistant.
2. Redémarre Home Assistant.

## Configuration

1. Dans Home Assistant, va à **Paramètres → Appareils et services → Ajouter une intégration**.
2. Sélectionne `Solax Installer Settings` et saisis l’adresse IP/le nom d’hôte ainsi que le mot de passe installateur de l’onduleur.
3. Après la configuration, l’hôte ou le mot de passe peuvent être mis à jour via **Configurer** dans l’intégration. Les paramètres installateur disponibles sont chargés directement depuis l’onduleur et affichés dans une liste déroulante avec la valeur actuelle, permettant de modifier les réglages sans connaître la clé.

## Services

L’intégration fournit des services pour récupérer et définir des paramètres installateur :

```yaml
service: solax_installateur_settings.set_installer_setting
data:
  setting: feed_in_limit
  value: 50
  # host: 192.168.1.100  # optionnel, requis lors de l’utilisation de plusieurs onduleurs
```

```yaml
service: solax_installateur_settings.get_installer_settings
data:
  # host: 192.168.1.100  # optionnel, requis lors de l’utilisation de plusieurs onduleurs
```

Les deux services prennent en charge plusieurs onduleurs ; dans ce cas, le champ `host` doit être défini pour sélectionner le bon client.

## Implémentation

La communication avec l’onduleur est gérée par le `SolaxInstallerClient` interne défini dans `custom_components/solax_installateur_settings/api.py`. L’API HTTP peut varier selon le modèle d’onduleur ; ajuste `api.py` si nécessaire.

