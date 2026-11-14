# ha-solax-installateur-settings

[English](README.md) | [Deutsch](README.de.md) | [Español](README.es.md)

Intégration personnalisée pour Home Assistant permettant de gérer les **paramètres installateur protégés par mot de passe** des onduleurs hybrides SolaX (Gen4/Gen5, p. ex. **X3-IES**) via **Modbus TCP**.

Le mot de passe installateur est écrit dans le registre de déverrouillage (registre holding `0x0000`) ; l’onduleur indique ensuite son état de verrouillage (registre input `0x0054`), ce qui permet de détecter immédiatement un mauvais mot de passe.

## Prérequis

- Home Assistant 2024.11 ou plus récent
- Accès Modbus TCP à l’onduleur (même IP/port que `solax_modbus`, port `502`, unit ID `1` par défaut)
- Le mot de passe installateur numérique (p. ex. `2014` basique ou `6868` avancé)

## Installation

1. Dans HACS, ajoutez le **dépôt personnalisé** `https://github.com/404GamerNotFound/ha-solax-installateur-settings` de type *Intégration*, installez `Solax Installer Settings` puis redémarrez Home Assistant.
2. Ou copiez `custom_components/solax_installateur_settings` dans votre dossier `custom_components` et redémarrez.

## Configuration

1. **Paramètres → Appareils et services → Ajouter une intégration → Solax Installer Settings**.
2. Saisissez l’hôte, le port, l’unit ID et le **mot de passe installateur** ; il est vérifié en déverrouillant l’onduleur.
3. Le **mode lecture seule** est actif par défaut ; désactivez-le via **Configurer** pour autoriser les modifications.

Des entités `number`/`select` sont créées pour la limite d’injection, le courant du disjoncteur principal, les courants batterie, le SoC minimum EPS, le sens des compteurs, le biais réseau et le shadow fix PV1–PV3, ainsi qu’un capteur d’état de verrouillage et des boutons de (dé)verrouillage. Détails et services : voir le [README anglais](README.md).
