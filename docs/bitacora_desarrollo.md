# Bitácora de desarrollo

## Commit: Agrega captura por BSSID y mejora reporte técnico

### Cambio técnico realizado
Se modificó el módulo de captura para registrar cada BSSID como una observación técnica independiente. También se incorporaron campos como banda, canal y tipo de radio cuando están disponibles en la salida de netsh.

### Relación con la tesis
Este cambio se relaciona con las secciones:
- 4.4.1 Arquitectura general
- 4.7 Variables
- 4.8 Procesamiento y análisis de datos
- Capítulo IV: Resultados y discusión

### Justificación académica
Un mismo SSID puede estar asociado a múltiples BSSID, especialmente en redes doble banda o con múltiples puntos de acceso. Tratar cada BSSID como unidad de observación mejora la trazabilidad del análisis técnico.

### Pendiente en la tesis
Actualizar la metodología para mencionar que la unidad técnica de observación puede ser el BSSID, no solamente el SSID.