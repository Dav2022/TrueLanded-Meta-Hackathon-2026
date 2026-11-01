# DF-042 — Matriz de elegibilidad y jerarquía de fuentes

**Fecha de revisión original:** 2026-10-29 (Costa Rica). **Adenda verificada:** 2026-10-31. **Estado:** auditoría técnica privada; no constituye dictamen jurídico ni autorización de envío.

## Jerarquía de fuentes

## ADENDA DF-072 — Revisión documental directa del Event Waiver

**Hallazgo:** el archivo del propietario `Event Waiver.pdf` comienza con el título
`Hackathon Terms & Conditions (“Official Rules”) and Event Waiver`, y contiene
reglas de participación, evaluación, titularidad, licencias y presentación.
Por tanto, la afirmación antigua de que **no teníamos el texto oficial** ya no es
correcta. No equivale a comprobar el registro electrónico de aceptación del usuario
en Cerebral Valley; esa aceptación permanece pendiente de verificación.

- **Official Rules disponibles y examinadas:** PASS documental.
- **Aceptación electrónica de las Official Rules en el portal:** NO VERIFICADA.
- **Secciones de derechos:** `Release of Information` y `Hackathon Submission`:
  titularidad del participante, pero licencia organizador amplia, mundial y perpetua;
  el material compartido no recibe garantía de confidencialidad.
- **Guía §4:** repositorio público, trabajo desarrollado durante el evento y derechos
  sobre el contenido; una copia ZIP privada no sustituye la URL pública exigida.
- **Guía §7:** video de 3 minutos, URL accesible, colaboradores completos,
  presentación antes de la hora límite.

**El resto de la matriz se conserva como registro histórico DF-042 y las notas
anteriores sobre waiver no disponible deben leerse en este nuevo contexto.**


**P1 — Guía del participante recibida por el propietario:** `Meta Global AI Developer Hackathon Participant Guide.pdf`, siete páginas. Apartados 3 (Schedule), 4 (Hackathon Rules), 7 (Submission Process), 8 (Judging Process). La guía está en los materiales privados del proyecto; NO está incluida en el repositorio competitivo.

**P2 — Páginas públicas actuales de los organizadores:**
- https://dev.meta.ai/events/global-hackathon
- https://cerebralvalley.ai/e/meta-ai-developer-hackathon
- https://cerebralvalley.ai/e/meta-ai-developer-hackathon/waiver — la visualización pública devuelve solamente “Loading...”; **no se recuperó el texto del waiver autenticado**.

**P3 — Términos API de Meta, actualizados 2026-10-09:** https://dev.meta.ai/legal/terms-of-service ; sección 4.1: según los términos, Meta no reclama titularidad de entradas/salidas entre partes, sujeto a restricciones y derechos de terceros. **Esto no otorga derechos sobre código ajeno ni constituye aprobación para publicar cualquier salida concreta.**

**P4 — `Meta Model API: Global AI Developer Hackathon Credit Terms` (3 páginas), entregado en el proyecto:** regula exclusivamente créditos; declara expresamente que la participación, el jurado y los premios están sujetos a las **Official Rules**, no a esos Credit Terms.

**P5 — Reporte del propietario de mensajes Discord (2026-10-29):** reivindica que el repositorio debe crearse el 26 de octubre o después. La guía no precisa fecha de creación de repositorio; esa exigencia se mantiene como **informe secundario**, pendiente del mensaje original/enlace y de las reglas aceptadas. No convertir esta evidencia indirecta en una cláusula verificada del reglamento.

## Requisitos operativos

| ID | Exigencia | Base | Evidencia disponible | Dictamen |
|---|---|---|---|---|
| EL-01 | Trabajo mostrado creado durante evento / identificar aportes nuevos | Guía §4; kickoff 26/10, construcción §3 27/10–04/11 | `NEW_WORK.md`, seis commits en repositorio aislado; proyectos preexistentes explícitamente excluidos | CONDICIONAL: revisión humana autoría y obras derivadas |
| EL-02 | Repositorio GitHub público en entrega | Guía §§4,7 | GitHub `Dav2022/TrueLanded-Meta-Hackathon-2026` permanece privado | **NO-GO** para entrega |
| EL-03 | URL de video demo accesible y duración tres minutos | Guía §7 | No existe video de envío aprobado; prototipos locales solamente | **NO-GO** |
| EL-04 | Uso significativo de modelos Meta | Guía §§1,8 | DF-039: Muse Spark 1.3, HTTP 200, 18 campos exactos verificados; recibo privado | PASS parcial; independencia de acceso jurado abierta |
| EL-05 | Derechos sobre todo el código y activos | Guía §4 | Escaneo original comercial 397 archivos comparables, cero SHA idénticos; prueba no excluye derivados ni permisos de terceros | **OPEN** |
| EL-06 | Registro durante evento (según Discord) | Informe Discord, no regla oficial extraída | GitHub API `created_at=2026-10-29T21:36:51Z` | Fecha demostrada; interpretación final de elegibilidad pendiente |
| EL-07 | Equipo y pista declarados | Guía §§4,7; Meta Indie Track | Repositorio preparado como Indie | Pendiente confirmar formulario y lista definitiva de colaboradores |
| EL-08 | Envío antes de cierre | Guía §7, Meta oficial | 2026-11-04 21:00 ET = 20:00 Costa Rica (EST tras cambio del 1/11) | Plazo próximo |
| EL-09 | Presentación sin marcas o activos de terceros no autorizados | Guía §4 y créditos §6.1 (créditos) | Uso textual descriptivo “Meta”, “Muse”; imágenes/logos requieren revisión separada | **OPEN** |
| EL-10 | Ausencia de autoautorizaciones aduaneras | Reglas generales/políticas; contrato de demo | Casos ficticios, emisor no autenticado, revisión humana obligatoria | PASS técnico |
| EL-11 | Rúbrica | Guía §8 | Impacto 30%; Meta AI 25%; profundidad/ejecución 20%; demo 25% | CONFIRMADO en guía |
| EL-12 | Oficial Rules aceptadas por el participante | Sitio Meta remite a Official Rules/waiver | Texto del waiver no accesible públicamente desde herramienta; no fue aportado documento aceptado | **OPEN crítico** |

## Interpretaciones y conflictos que NO se deben ocultar

1. **“Open source: Repositories must be public”** está en la guía. Poner un repositorio privado como único enlace de envío no satisface esa instrucción.
2. Publicar sin licencia permite leer código, pero no concede necesariamente permisos de uso, modificación y redistribución propios de una licencia abierta. **Elegir licencia exige aprobación del titular**; no fabricar permiso por defecto.
3. **Un ZIP independiente no reemplaza el requisito de repositorio público**; sirve como prueba adicional para el jurado.
4. El GitHub actual se creó después del kickoff, pero **su historial incluye una reproducción histórica del modelo**. Borrar archivos del último commit no elimina los objetos anteriores de Git.
5. La demostración DF-040 reproduce una respuesta auténtica anterior con verificación local, sin firma criptográfica independiente de Meta. No afirmar autenticación externa de proveedor.
6. El crédito promocional de 150 USD y su uso opcional **no exigen gastar** para competir. No usar los Credit Terms como sustituto de las Official Rules.

## Decisión preliminar

**GO:** pruebas privadas, revisión de derechos, documentación de aportes nuevos, preparación de una copia de publicación con historial limpio, plan de video y formulario.

**NO-GO:** hacer público el GitHub existente, enviar el formulario, fijar una licencia, divulgar recibos originales o afirmar que las Official Rules fueron verificadas, hasta resolver las puertas correspondientes.
