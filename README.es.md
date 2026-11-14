# ha-solax-installateur-settings

[English](README.md) | [Deutsch](README.de.md) | [Français](README.fr.md)

Integración personalizada de Home Assistant para gestionar los **ajustes de instalador protegidos por contraseña** de inversores híbridos SolaX (Gen4/Gen5, p. ej. **X3-IES**) mediante **Modbus TCP**.

La contraseña de instalador se escribe en el registro de desbloqueo (registro holding `0x0000`); el inversor informa después su estado de bloqueo (registro input `0x0054`), por lo que una contraseña incorrecta se detecta de inmediato.

## Requisitos

- Home Assistant 2024.11 o posterior
- Acceso Modbus TCP al inversor (la misma IP/puerto que usa `solax_modbus`, puerto `502`, unit ID `1` por defecto)
- La contraseña numérica de instalador (p. ej. `2014` básica o `6868` avanzada)

## Instalación

1. En HACS añade el **repositorio personalizado** `https://github.com/404GamerNotFound/ha-solax-installateur-settings` como *Integración*, instala `Solax Installer Settings` y reinicia Home Assistant.
2. O copia `custom_components/solax_installateur_settings` a tu carpeta `custom_components` y reinicia.

## Configuración

1. **Ajustes → Dispositivos y servicios → Añadir integración → Solax Installer Settings**.
2. Introduce host, puerto, unit ID y la **contraseña de instalador**; se verifica desbloqueando el inversor.
3. Por defecto está activo el **modo solo lectura**; desactívalo en **Configurar** para permitir cambios.

Se crean entidades `number`/`select` para límite de inyección, corriente del interruptor principal, corrientes de batería, SoC mínimo EPS, dirección de los medidores, bias de red y shadow fix PV1–PV3, además de un sensor de estado de bloqueo y botones para desbloquear/bloquear. Detalles y servicios: ver [README en inglés](README.md).
