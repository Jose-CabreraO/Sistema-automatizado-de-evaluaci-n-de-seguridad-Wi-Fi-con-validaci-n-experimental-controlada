# Decisiones técnicas del proyecto

## Decisión 1: enfoque pasivo y no intrusivo

El sistema se mantiene dentro de un enfoque pasivo. No ejecuta ataques, no captura credenciales, no intercepta tráfico privado, no valida contraseñas y no realiza pruebas de penetración.

Esta decisión se alinea con la delimitación de la tesis y con los aspectos legales definidos en el documento académico.

## Decisión 2: uso de Windows y netsh

El sistema utiliza el comando:

`netsh wlan show networks mode=bssid`

La elección se justifica porque la tesis propone una herramienta local orientada a entornos Windows, comúnmente utilizados en pequeñas organizaciones.

## Decisión 3: BSSID como observación técnica independiente

Durante las pruebas reales se observó que un mismo SSID puede tener múltiples BSSID, especialmente en redes doble banda o con múltiples puntos de acceso.

Por ello, el sistema registra cada BSSID como una observación técnica independiente, conservando SSID, autenticación, cifrado, señal, canal, banda y tipo de radio.

Esta decisión mejora la trazabilidad del análisis y permite diferenciar infraestructura legítima de posibles condiciones anómalas.

## Decisión 4: reporte PDF como evidencia técnica

El reporte PDF se considera evidencia técnica generada por el sistema. Debe incluir tabla de resultados, hallazgos principales, recomendaciones priorizadas, trazabilidad y limitaciones del análisis.

El reporte no debe presentarse como auditoría integral de seguridad.