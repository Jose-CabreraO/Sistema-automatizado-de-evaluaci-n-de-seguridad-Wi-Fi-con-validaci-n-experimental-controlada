# Contexto de tesis para desarrollo del sistema

## Título

Sistema automatizado de evaluación de seguridad Wi-Fi con validación experimental controlada.

## Contexto académico

Este repositorio corresponde al desarrollo técnico de una tesis de Ingeniería Informática. La tesis propone un sistema local desarrollado en Python para Windows, orientado a la evaluación técnica de redes Wi-Fi mediante observación pasiva de parámetros visibles.

El sistema utiliza como fuente primaria la salida del comando:

`netsh wlan show networks mode=bssid`

## Alcance funcional permitido

El sistema puede:

- Capturar redes visibles desde Windows.
- Procesar la salida de `netsh wlan show networks mode=bssid`.
- Extraer SSID, BSSID, autenticación, cifrado, intensidad de señal, canal, banda y tipo de radio.
- Tratar cada BSSID como una observación técnica independiente.
- Normalizar parámetros observables.
- Calcular un puntaje WSS de severidad técnica.
- Clasificar el resultado en niveles cualitativos.
- Generar JSON técnico.
- Generar reporte PDF.
- Incluir hallazgos principales.
- Incluir recomendaciones técnicas basadas únicamente en los datos capturados.
- Incluir limitaciones del análisis.

## Alcance no permitido

El sistema no debe:

- Ejecutar ataques.
- Usar modo monitor.
- Capturar paquetes.
- Interceptar tráfico.
- Capturar credenciales.
- Validar contraseñas.
- Realizar fuerza bruta.
- Presentarse como auditoría integral.
- Usar herramientas ofensivas.
- Inventar datos no capturados.
- Modificar el modelo WSS sin justificación académica previa.

## Modelo WSS base

El modelo base definido en la tesis es:

`Pb = (Sauth + Scif) / 2`

`Score = Pb × Fexp × 10`

Donde:

- `Sauth` representa la severidad asociada al mecanismo de autenticación.
- `Scif` representa la severidad asociada al esquema de cifrado.
- `Fexp` representa el factor de exposición técnica derivado de la intensidad de señal.

## Valores definidos en la tesis

Autenticación:

- WPA3-Personal / SAE: 0.1
- WPA2-Personal: 0.3
- WPA / WPA-TKIP: 0.7
- Red abierta / OPEN: 1.0

Cifrado:

- CCMP / AES: 0.1
- TKIP: 0.8
- WEP: 0.9
- NONE: 1.0

Exposición técnica:

- Señal mayor o igual a 80%: 1.0
- Señal entre 50% y 79%: 0.8
- Señal menor a 50%: 0.5

## Campos que no deben cambiarse

Los nombres de campos actuales deben mantenerse para no romper el flujo entre módulos:

- `ssid`
- `bssid`
- `autenticacion`
- `cifrado`
- `senal`
- `canal`
- `banda`
- `tipo_radio`
- `resultado`
- `vector_wss`
- `puntaje_final`
- `nivel_riesgo`

## Reglas para desarrollo

1. No cambiar el modelo WSS sin autorización.
2. No agregar funcionalidades que no estén respaldadas por la tesis.
3. No agregar análisis ofensivo.
4. No incluir datos reales hardcodeados.
5. No subir reportes reales, JSON reales ni salidas reales de `netsh`.
6. Trabajar en cambios pequeños y revisables.
7. Explicar cada cambio técnico realizado.
8. Mantener el sistema como herramienta local, pasiva y no intrusiva.