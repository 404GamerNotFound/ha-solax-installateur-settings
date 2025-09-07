# ha-solax-installateur-settings

Integración personalizada de Home Assistant para gestionar los ajustes de instalador en inversores SolaX mediante la API HTTP local. Permite cambiar parámetros de instalador sin salir de Home Assistant.

## Requisitos previos

- Una instalación funcional de Home Assistant
- Acceso a la red local del inversor
- La contraseña de instalador del inversor

## Instalación

### Via HACS

1. En HACS agrega el **Repositorio Personalizado** `https://github.com/404GamerNotFound/ha-solax-installateur-settings` como tipo *Integration*.
2. Después de añadirlo, busca `Solax Installer Settings` en HACS e instálalo.
3. Reinicia Home Assistant.

### Instalación manual

1. Copia el directorio `custom_components/solax_installateur_settings` al directorio `custom_components` de tu instalación de Home Assistant.
2. Reinicia Home Assistant.

## Configuración

1. En Home Assistant ve a **Configuración → Dispositivos y Servicios → Agregar integración**.
2. Selecciona `Solax Installer Settings` e introduce la dirección IP/nombre de host y la contraseña de instalador del inversor.
3. Tras la configuración, el host o la contraseña se pueden actualizar mediante **Configurar** en la integración. Los parámetros de instalador disponibles se cargan directamente desde el inversor y se muestran en una lista desplegable con el valor actual, lo que permite cambiar ajustes sin conocer la clave. De forma predeterminada la integración funciona en modo *solo lectura* para evitar cambios accidentales; puede desactivarse en las opciones de la integración para permitir modificaciones.

## Servicios

La integración proporciona servicios para obtener y establecer parámetros de instalador:

```yaml
service: solax_installateur_settings.set_installer_setting
data:
  setting: feed_in_limit
  value: 50
  confirm: true
  # host: 192.168.1.100  # opcional, necesario cuando se usan varios inversores
```
`confirm: true` es obligatorio como medida de seguridad; las llamadas sin él se rechazan.

```yaml
service: solax_installateur_settings.get_installer_settings
data:
  # host: 192.168.1.100  # opcional, necesario cuando se usan varios inversores
```

Ambos servicios admiten múltiples inversores; en ese caso debe establecerse el campo `host` para seleccionar el cliente correcto.

## Implementación

La comunicación con el inversor se gestiona mediante el `SolaxInstallerClient` interno definido en `custom_components/solax_installateur_settings/api.py`. La API HTTP puede variar según el modelo de inversor; ajusta `api.py` si es necesario.

