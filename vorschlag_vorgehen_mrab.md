# Quellenbewertung:
- Object serialisation and deserialisation using xml
Einfach nur Implementierung und Interface-Design für einen einzelnen XML-Serializer. Nicht besonders relevant,
aber evtl. zur Bewertung der Usability von getesteten Libraries verwendbar.

- Performance evaluation of using Protocol Buffers in the Internet of Things communication
Gute Quelle. Behandelt "nur" JSON/BSON und Protobuf, dafür aber sehr gut mMn. Es gibt eine Beschreibung der Methodik und der Ergebnisse.
Viele konkrete Zahlen und Bewertungen. Ist zwar auf IoT spezialisiert, aber bestimmt in Teilen transferierbar.

- Perfomance evaluation of Java, JavaScript and PHP serialization libraries for XML, JSON and binary formats
Kann nicht mehr zugreifen, weil Springer. Schade. War glaub ne super Quelle, zumal sie exakt die 4 Formate behandelt, die wir auch
abklappern wollen.

- Streaming Technologies and Serialization Protocols: Empirical Performance Analysis
Sehr breite, ausführliche Übersicht über 10 Formate. Gibt eine sinnvolle Liste an Bewertungsmetriken, darunter:
    - Object Creation Latency
    - Object Creation Throughput
    - Compression Ratio
    - Serialization Latency
    - Deserialization Latency
    - Serialization Throughput
    - Deserialization Throughput
    - Transmission Latency (nur für Streaming-Protokolle)
    - Transmission Throughput
    - Total Latency
    - Total Throughput
    - Effect of Batch size on Throughput
Auch gute Datenlage, viele Tabellen, Messungen und Zahlen. Sehr sehr viele Quellen, die man sich auch mal ankucken kann.

- A Specialized Architecture for Object Serialization with Applications to Big Data Analytics
Katastrophale Textgüte. Rechtschreib- und Grammatikfehler überall. Nur ein Vorschlag, keine konkrete Implementierung.
Müllquelle.


# Zur Performanz-Messung:
Verschiedene Implementierungen:
Wie schnell ist Implementierung X oder Y in Sprache Z, wie schnell sind Implementierungen sprachübergreifend?
-> Messungen

Verschiedene Algorithmen/Formate:
Wie schnell ist Format X gegenüber Format Y wenn die Implementierungsgüte gleich ist?
-> Big O, evtl. noch Skalierungskonstanten

Vorschlag zum Vorgehen:
Eine Person misst Implementierungsgüte, während andere Person verschiedene Algorithmen/Formate testet. Hoffentlich können durch die Messungen zur Implementierungsgüte
Skalierungsfaktoren bestimmt werden, über die der Vergleich der verschiedenen Algorithmen/Formate "fairer" geschieht.

