# SIAL Basket — LEEME / Historial de versiones

Estado: registro de conciliación, 2026-11-03. Este documento no modifica la aplicación ni los archivos MASTER/SDC.

## Política de versiones
- Mantener un único `LEEME.md` acumulativo en la raíz del paquete distribuido, junto a `index.html`.
- Para cada versión: base, cambios, funciones conservadas, pruebas realizadas, pendientes y advertencias.
- Sin autorización expresa, no alterar la geometría ni el orden de controles de pantallas congeladas A1/A2/A3.
- Sincronizar la versión mostrada en barra, pestaña HTML, manifiesto, caché y LEEME. No usar el nombre del ZIP como única fuente de versión.

## Histórico verificado en archivos disponibles

### v0.43 — Base visual congelada (ZIP recibido)
- Archivo: `SIAL_PWA_LAB_v43_A1_BOTONES_EN_FILA_LAB(1).zip`.
- `LEEME.txt`: corrección de selector CSS de navegación A1; botones Atrás/Siguiente y Atrás/Confirmar e iniciar en una fila.
- Título HTML: `PWA LAB v0.43`.
- Referencia de disposición visual; no contiene opción `Delegado-Aux`.

### v0.44 — Ajustes arbitrales (ZIP disponible)
- Base v0.43.
- `LEEME.txt`: mandos inferiores, acciones ocultas, botón ARB, tiempos fuera por mitad, prórroga, bloqueo de siguiente cuarto y Delegado-Aux.
- Secuencias de faltas: explícitamente pendientes.
- Título HTML: `PWA LAB v0.44`.

### v0.45 — Revisión parcial (ZIP disponible)
- `LEEME.txt`: modalidades 5x5/3x3, tiempos fuera 3x3, prórroga, edición provisional de oficiales y quinta falta con sustitución.
- Pendientes en esta versión: secuencias completas de faltas.
- **Incidencia:** el título HTML todavía dice `PWA LAB v0.44`, aunque el ZIP se llama v45.
- **Incidencia:** opción Delegado-Aux repetida en datos de asistente A (verificado en código).

### v0.46.3 — Revisión funcional (ZIP disponible)
- Archivo: `SIAL_PWA_CAMPO_LAB_v0463_REVISION.zip`.
- Usuario confirma que A1/A2/A3 abren y que secuencias de foules registran eventos.
- Pendiente comparar controles de A2, MÁS ACCIONES, ARB y mensajes de tiempo fuera contra v0.44 y validar exhaustivamente 5x5/3x3.
- Pendiente validar persistencia offline, J6 y rosters reales.
- No considerar versión de campo aprobada hasta pruebas en tabletas.

## Decisiones vigentes por consolidar
1. Base visual: v0.43, respetando ajustes congelados de v0.44.
2. A1 (1/3): 5x5 y 3x3 dinámicos; no perder reglas de tiempos fuera.
3. A1 (2/3): Delegado-Aux una sola vez.
4. A1 (3/3): CAMBIOS edita oficiales sin regresar a (2/3).
5. A2: botones inferiores y MÁS ACCIONES aprobados, ARB en tiempo fuera, secuencias táctiles de foules, tiros libres, faltas de equipo y expulsiones.
6. Título: `SIAL BASKET · vX.Y.Z`, sin `CAMPO LAB` en barra; misma versión en pestaña.
7. LOGO y marca de agua sin alterar legibilidad.
8. J6: dos tabletas Android, acceso de campo sin login, importación local de rol/rosters y operación offline validada.

## Pendientes técnicos
- Comparación detallada de v0.46.3 contra v0.44, incluyendo comportamiento (no solo presencia de cadenas).
- Pruebas de interfaz y secuencias de sanciones con árbitros.
- Verificación en ambas tabletas del giro horizontal y recuperación de escala.
- Archivo JSON J6 con identificadores validados contra InscGposTorn; no inventar identificadores.

## Auditoría comparativa v0.44 ↔ v0.46.3 (2026-11-03)
- **Crítico:** v0.46.3 cambió indebidamente el conteo de tiempos fuera 5×5 **por mitad (2/3)** de v0.44 a conteo **por cuarto**. Recuperar regla congelada; manejar 3×3 y prórrogas por separado.
- **Crítico:** reinicio del reloj pasó de duración configurada a `600` segundos fijos. Restaurar duración variable.
- **Pendiente:** cotejar en navegador controles inferiores, MÁS ACCIONES, botón ARB y mensajes de tiempo fuera; inspección de cadenas no prueba equivalencia.
- **Versión:** HTML v0.46.3 correcto, pero referencia al service worker `?v=040` desactualizada; sincronizar manifiesto y caché.
- **Conservar:** asistente táctil de faltas de v0.46.3, y edición A1, sujetos a pruebas funcionales.
- Detalle: `SIAL_COMPARACION_v044_vs_v0463.md`. Sin cambios al código ni archivos MASTER/SDC.

## v0.46.4 — Consolidación técnica (2026-11-03)
- Base de código: v0.46.3. No se reemplazaron las pantallas A1, A2, A3.
- Recuperado conteo de tiempos fuera **5×5 por mitades**: 2 por equipo primera mitad y 3 segunda mitad, duración 60 s.
- 3×3: 1 tiempo fuera por equipo y periodo, duración 30 s. Prórroga con contador propio.
- Reloj: **Reiniciar reloj** y **Siguiente cuarto** utilizan los minutos seleccionados en A1 en lugar de 600 segundos fijos.
- Eliminado selector obsoleto de tiempos fuera por cuarto en A1, que contradecía la regla congelada.
- Sincronizada versión v0.46.4 en título, manifiesto, URL de inicio, caché y registro Service Worker.
- Conservados los controles y el asistente táctil de foules existentes en v0.46.3.
- Verificado: sintaxis de scripts JS con Node; NO verificado: ejecución en navegador/tabletas, exactitud arbitral, persistencia offline, importación J6.
- **Pendiente:** comprobar condiciones especiales de tiempos fuera en últimos dos minutos del cuarto periodo y lógica real de prórrogas; no declarar versión oficial.
- **Regla de entrega:** este LEEME debe estar en la raíz de cada ZIP de revisión y actualizarse acumulativamente.


## v0.46.5 — 2026-11-03
- Indicador visible **EXP** en la ficha para descalificación directa y acumulación disciplinaria, separado de las cinco marcas de faltas.
- Quinta falta: se conservan cinco marcas; bloqueo de elegibilidad y sustitución obligatoria.
- Sustitución obligatoria: jugador saliente preseleccionado y resaltado; solo elegir entrante.
- A1 (2/3): cada lista de asistente ofrece entrenador, asistente, Sin asistente y Delegado-Aux.
- Se conservan botones y distribución existentes de A2; la restauración exacta de controles congelados distintos de v0.46.4 requiere cotejo adicional con referencia visual/código.
- Pendiente prueba funcional real en PC y tabletas; no usar como acta oficial.


## v0.46.6 — Recuperación de controles congelados A2 (2026-11-03)
- Fuente de comparación: `SIAL_PWA_LAB_v44_AJUSTES_ARBITROS_REVISION.zip` y base funcional v0.46.5.
- A2: **SIGUIENTE CUARTO** y **▶ INICIAR/PAUSAR** en fila inferior; reloj y marcador permanecen en barra superior.
- **MÁS ACCIONES**: REINICIAR RELOJ, REINICIAR PARTIDO, FINALIZAR PARTIDO (este último visible solo al terminar el tiempo reglamentario).
- Retirados de MÁS ACCIONES los botones ENTRADA/SALIDA introducidos en versiones posteriores; las sustituciones continúan mediante SUST.
- Se conservan flechas de continuidad, botones principales, ARB en tiempo fuera, faltas táctiles, marcas de 5 faltas, EXP y sustitución obligatoria de v0.46.5.
- Se sincronizan título, manifiesto y service worker a v0.46.6.
- Verificación estática: existencia única de IDs, sintaxis JavaScript y estructura del paquete. Pendiente prueba real en PC y tabletas; no es versión oficial de campo.


## v0.46.7 — Foto ampliada e ícono PWA
- Foto en A1: ancho de dos fichas y alto de tres; posicionamiento adaptable a PC y tablet, con ajuste al espacio visible.
- Ícono de instalación PWA: logo transparente de barra de título, 192 y 512 px.
- Actualizados versión visible, pestaña, manifiesto y caché de service worker.
- No se modificaron reglas de juego, controles congelados ni datos MASTER.
