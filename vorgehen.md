# Vorgehen

Testdaten:
- Key-Value pairs
- Flache, primitive Listen
- Zusammengesetzte, komplexe Datentypen

Menge: 1-2 stellig GB

Abgrenzung und Zuweisen zu Anwendungsfällen ("bei Streaming braucht man besonders X")
Testdaten können selbst generiert werden (Kein "der Datensatz" für Messungen)

Metriken:
- Messbar:
  - Compression Ratio
  - Throughput
  - Batching Speedup
- Nicht messbar:
  - Lesbarkeit
  - Wartbarkeit/Usability

ToDo:
- Matthias:
  - Quellensuche: Implementierungsgüte, welche gut, welche nicht, Vergleich, etc.
  - Implementierung:
    - Datengenerierung
- Fabian:
  - Implementierung:
    - Konzept entwickeln, wie strukturiert getestet/gemessen werden kann
    - Datengenerierung
    - Python
- Shared:
