# DF-042 — Propiedad intelectual y riesgo del historial Git

**Estado:** auditoría técnica con sign-off legal pendiente del propietario. No autoriza una licencia pública.

## Resultado de exploración sobre el repositorio privado existente

- HEAD revisado: `4bbfb4df9e9c7c078da0cde947dc00b069bc885b`.
- 58 archivos versionados; seis commits históricos, 91 objetos Git inspeccionados en auditoría privada.
- Cero coincidencias de firmas de secreto de alta confianza en los blobs históricos evaluados (cobertura de patrones limitada).
- Cero coincidencias de SHA-256 para 58 archivos competitivos contra **397 archivos de código/documentos comparables del repositorio comercial**, excluidos archivos muy grandes o ciertas carpetas; **no prueba no derivación**.
- Tres archivos actuales contienen nombres de estructuras de captura privada como referencias de código o documentación; **no significa que el cuerpo privado esté incluido**.
- Tres archivos actuales contienen cadenas de identificación del visor histórico de respuesta derivada; **requieren revisión especial de permiso de publicación**.
- No se detectó `UNTRUSTED_HTTP_BODY_PRIVATE.bin` entre los archivos versionados.
- Siete archivos históricos dentro de `viewer/` se distribuyen todavía en HEAD, aunque el Judge Kit DF-041 **los excluye**.
- Un `git rm viewer/` ordinario conservaría esa historia en los objetos Git antiguos.

## Tres planos jurídicamente distintos

1. **Código comercial anterior** (TrueLanded original): mantener privado, no duplicar y no publicar parte sustancial sin decisión expresa sobre alcance. Las coincidencias de hash no prueban autoría ni independencia.
2. **Código nuevo del hackatón**: puede publicarse si el titular confirma su autoría/licenciabilidad y que no incorpora terceros con permisos incompatibles. `NEW_WORK.md` traza commits competitivos, pero no es una cesión de derechos.
3. **Salida y evidencia de Meta API**: los términos de Meta dejan los derechos de Content al usuario *entre las partes*, sujetos a derechos de terceros y restricciones; evitar reproducir recibos privados, IDs, tokens, metadatos personales, claves o contenido sensible. El ejemplo es sintético y local, pero las licencias de sus fragmentos requieren revisión.

## Liberación del historial: decisiones alternativas

**Alternativa A — recomendada para minimizar exposición:** repositorio de entrega nacido durante el período, con **snapshot Git de una única raíz nueva** a partir del Judge Kit verificado, más `NEW_WORK.md`, permisos y licencia aprobados. Documentar la procedencia por hashes y commits del repositorio privado original. Requiere comprobar que cumpla la eventual regla original sobre el repositorio creado después del kickoff. No mentir sobre fecha ni historial.

**Alternativa B:** publicar el repositorio actual si cada archivo y **cada blob de todos los commits previos** supera revisión jurídica/privacidad. Es más costoso y puede revelar trabajo histórico fuera del alcance de la entrega.

**Alternativa C:** reescribir el historial en el repositorio creado 29/10 y forzar push de un snapshot saneado, con un backup verificable y autorización explícita del propietario. **Operación destructiva sobre historial remoto, no autorizada en DF-042. No ejecutarla automáticamente.**

## Casillas que el titular debe declarar antes de GO

- [ ] Tiene derechos para licenciar código competitivo y todos los fragmentos derivados; empleadores, clientes y colaboradores no conservan derechos que impidan la publicación.
- [ ] Aprobó una licencia concreta (p. ej. MIT, Apache-2.0 u otra compatible), conscientemente y con claridad del alcance.
- [ ] Acepta liberar únicamente el subconjunto verificado; el núcleo comercial no se concede bajo esa licencia.
- [ ] No se publican recibos privados DF-039, API key, créditos ni datos de terceros.
- [ ] Confirmó originalidad y fecha de implementación, y distinguió con honestidad infraestructura anterior de contribuciones nuevas.
- [ ] Aprobó el comportamiento de marca/nombre en el video y el repositorio.
- [ ] Se revisó texto auténtico de Official Rules / waiver de la cuenta aceptada.

**Bloqueos técnicos restantes:** licencia todavía no otorgada; visor derivado en historia de repositorio actual; publicación sin GO expreso.
