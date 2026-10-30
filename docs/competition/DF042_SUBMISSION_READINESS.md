# DF-042 — Decisiones de entrega y narrativa para el jurado

**Meta competitiva:** Track Indie Developer, tema “Build for Your World”.
**Promesa técnica:** “Muse reads the evidence. TrueLanded decides which proof to get next — and shows what changes before you act.”

## Campos que podremos preparar para el portal

**Proyecto:** TrueLanded — Evidence-to-Decision Engine

**Descripción breve:** sistema de planificación de evidencia para comercio internacional, con extracción de literales documentales propuesta por Muse Spark 1.3, verificación contra el origen, priorización determinista de evidencias faltantes y cascadas contrafactuales auditables.

**Problema concreto:** contradicciones entre factura, empaque y especificaciones técnicas retrasan la preparación de expedientes aduaneros; el usuario necesita identificar qué documento debería solicitar a continuación y qué incertidumbre resolverá.

**Solución demostrable:** tres momentos visuales conectados: Evidence Spotlight, Next Best Proof y Counterfactual Cascade. Emplea solamente documentos ficticios, no toma decisiones regulatorias vinculantes, no reemplaza al agente aduanero ni al regulador.

**Meta AI integrado:** se observó solicitud autorizada de Muse Spark 1.3 con HTTP 200 y 18/18 valores extraídos concordantes con la fuente (DF-039). La captura permanece privada. El recorrido offline público reproduce una respuesta simulada y nunca la presenta como nueva inferencia real.

**Distinción de aportes:** módulos creados durante el período competitivo, registros de procedencia y commits. El núcleo comercial preexistente no se distribuye; verificar independencia de código derivado y permisos del titular antes de publicar.

**Pruebas:** repositorio de desarrollo 108/108; Judge Kit aislado 93/93 Windows y Ubuntu, fuente sin Git ni credenciales. Hashes autoemitidos; nunca afirmar firmas de Meta.

**Repositorio público:** PENDIENTE.
**Video 3 min, accesible:** PENDIENTE.
**Integrantes registrados:** PENDIENTE DE FORMULARIO.
**Reglas originales/waiver revisados:** PENDIENTE.

## Tres demostraciones — no deben confundirse

| Variante | Se puede repetir sin claves | ¿Es inferencia Meta real? | ¿Puede difundirse? |
|---|---|---|---|
| Simulación DF-037 y Judge Kit | Sí | No: fixture local con forma del contrato Muse | Solo tras licencia y reglas |
| Revisión privada DF-040 | No: necesita DF-039 privado | Reproduce una solicitud real anterior; NO nueva inferencia del navegador | No sin autorización de evidencia |
| Nueva llamada autenticada mediante CLI | Necesita clave Meta y aceptación de costo por operador | Sí, si HTTP/contrato/fuentes se verifican | Solo registro derivado saneado y aprobado |

## Ruta de cierre sin trabajo innecesario

1. Verificar las Official Rules aceptadas y resolver el requisito de repositorio público, evidencia de creación y formato de enlaces.
2. Obtener aprobación de licencia y IP, seleccionar historial saneado o repositorio nuevo.
3. Crear repositorio público **solo después de aprobación expresa**, con README, NEW_WORK, pruebas sin clave, aviso de limitaciones y demo sintética.
4. Ejecutar `RUN_JUDGE_CHECKS.py` desde GitHub público y confirmar accesibilidad anónima.
5. Preparar/video de tres minutos: 25 s problema, 35 s Evidence Spotlight, 40 s Next Best Proof, 40 s Counterfactual Cascade, 25 s límite real de Meta/replay, 15 s pruebas y conclusión. **Guion no es video**.
6. Completar entrega mediante CV antes del 4/11/2026 a las 20:00 Costa Rica (9 p. m. ET); comprobar que usuario y jueces puedan abrir video/URL.

## Aprobación de publicación

**NO-GO** hasta que todo: [licencia y derechos], [texto auténtico de reglas], [historial sin material reservado], [repo anónimo accesible], [video listo], [formulario confirmado].
