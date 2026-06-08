# Prompts aprobados para Codex

## Regla general

Codex debe leer primero `docs/contexto_tesis.md` antes de proponer cambios.

## Restricciones

- No modificar el modelo WSS sin autorización.
- No agregar funcionalidades ofensivas.
- No cambiar nombres de campos existentes.
- No incluir datos reales hardcodeados.
- No subir PDF, JSON, capturas o salidas reales de netsh.
- No modificar archivos fuera del alcance indicado.

## Prompt base para tareas de código

Lee primero `docs/contexto_tesis.md`.

Trabaja únicamente en el archivo indicado por el usuario.

No modifiques otros archivos.

Respeta el alcance académico de la tesis:
- sistema local en Python;
- entorno Windows;
- observación pasiva;
- captura mediante netsh;
- cálculo WSS;
- generación de JSON/PDF;
- sin ataques, sin captura de credenciales, sin interceptación de tráfico.

Antes de finalizar, explica:
1. qué archivo modificaste;
2. qué cambios hiciste;
3. qué parte de la tesis respalda esos cambios;
4. cómo probarlos.