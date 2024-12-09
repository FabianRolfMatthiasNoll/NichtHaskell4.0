import json
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import os

# Load results
with open("serialization_test_results/results.json", "r") as file:
    data = json.load(file)

separate_mode = True  # Ändere hier zwischen True (getrennt) und False (kombiniert)
labels_as_legend = False  # Nur relevant bei separate_mode=True. True = Labels als Legende, False = Labels unter dem Diagramm

# Output-Verzeichnis erstellen
if separate_mode:
    output_dir = "exported_charts_separate"
else:
    output_dir = "exported_charts_combined"
os.makedirs(output_dir, exist_ok=True)

# Daten nach Dataset gruppieren
datasets = {}
for item in data[1:]:
    dataset_name = item["Dataset"]
    if dataset_name not in datasets:
        datasets[dataset_name] = []
    datasets[dataset_name].append(item)

# Farbschema für Protokolle
protocol_colors = {
    "JSON": "blue",
    "XML": "orange",
    "MessagePack": "green",
    "ProtoBuf": "red",
}


# Funktion zum Erstellen von Diagrammen
def create_chart(dataset_name, protocols, separate_mode):
    protocols_sorted = sorted(protocols, key=lambda x: x["Protocol"])
    protocols_list = [p["Protocol"] for p in protocols_sorted]
    serialization_times = [
        p["Average Serialization Time (s)"] for p in protocols_sorted
    ]
    deserialization_times = [
        p["Average Deserialization Time (s)"] for p in protocols_sorted
    ]
    compression_ratios = [p["Compression Ratio"] for p in protocols_sorted]

    figures = []

    if separate_mode:
        # Serialisierungszeiten
        fig1, ax1 = plt.subplots(figsize=(10, 6))
        colors = [protocol_colors[p] for p in protocols_list]
        bars = ax1.bar(protocols_list, serialization_times, color=colors)
        ax1.set_title(f"Serialization Times for {dataset_name}")
        ax1.set_ylabel("Time (s)")

        if labels_as_legend:
            ax1.legend(bars, protocols_list, loc="upper right")
        else:
            ax1.tick_params(axis="x")

        figures.append((f"{dataset_name}_serialization", fig1))

        # Deserialisierungszeiten
        fig2, ax2 = plt.subplots(figsize=(10, 6))
        bars = ax2.bar(protocols_list, deserialization_times, color=colors)
        ax2.set_title(f"Deserialization Times for {dataset_name}")
        ax2.set_ylabel("Time (s)")

        if labels_as_legend:
            ax2.legend(bars, protocols_list, loc="upper right")
        else:
            ax2.tick_params(axis="x")

        figures.append((f"{dataset_name}_deserialization", fig2))

        # Kompressionsraten
        fig3, ax3 = plt.subplots(figsize=(10, 6))
        bars = ax3.bar(protocols_list, compression_ratios, color=colors)
        ax3.set_title(f"Compression Ratios for {dataset_name}")
        ax3.set_ylabel("Compression Ratio")

        if labels_as_legend:
            ax3.legend(bars, protocols_list, loc="upper right")
        else:
            ax3.tick_params(axis="x")

        figures.append((f"{dataset_name}_compression", fig3))

    else:
        # Kombinierte Balkendiagramme für Zeiten
        fig1, ax1 = plt.subplots(figsize=(10, 6))
        width = 0.4
        x = range(len(protocols_list))
        ax1.bar(
            x, serialization_times, width, label="Serialization Time (s)", color="blue"
        )
        ax1.bar(
            [i + width for i in x],
            deserialization_times,
            width,
            label="Deserialization Time (s)",
            color="orange",
        )
        ax1.set_title(f"Serialization and Deserialization Times for {dataset_name}")
        ax1.set_xticks([i + width / 2 for i in x])
        ax1.set_xticklabels(protocols_list)
        ax1.set_ylabel("Time (s)")
        ax1.legend()
        figures.append((f"{dataset_name}_combined_times", fig1))

    return figures


def create_combined_compression_chart(datasets):
    fig, ax = plt.subplots(figsize=(14, 8))

    dataset_names = list(datasets.keys())
    protocols = list(protocol_colors.keys())

    # Anzahl der Protokolle und Datensets
    protocol_count = len(protocols)
    dataset_count = len(dataset_names)

    # Breite der Balkengruppen
    group_width = 0.8  # Breite jeder Datensatzgruppe
    bar_width = group_width / protocol_count  # Breite jedes Balkens in der Gruppe

    # x-Positionen für Balken berechnen
    x_positions = []
    y = []
    colors = []

    for i, dataset_name in enumerate(dataset_names):
        start = i * (group_width + 0.2)  # Abstand zwischen Gruppen
        for j, protocol in enumerate(protocols):
            x_positions.append(start + j * bar_width)
            # Hole Kompressionsrate, falls vorhanden, sonst 0
            protocol_data = next(
                (p for p in datasets[dataset_name] if p["Protocol"] == protocol), None
            )
            y.append(protocol_data["Compression Ratio"] if protocol_data else 0)
            colors.append(protocol_colors[protocol])

    # Gruppenmitten für Dataset-Namen berechnen
    group_centers = [
        i * (group_width + 0.2) + (group_width / 2) - (bar_width / 2)
        for i in range(dataset_count)
    ]

    # Balken zeichnen
    bars = ax.bar(x_positions, y, color=colors, width=bar_width, edgecolor="black")

    # Gruppennamen unter der x-Achse
    ax.set_xticks(group_centers)
    ax.set_xticklabels(dataset_names, rotation=90)
    ax.set_xlabel("Dataset")
    ax.set_ylabel("Compression Ratio")
    ax.set_title("Compression Ratios Grouped by Dataset")

    # Legende für Protokolle
    handles = [
        plt.Rectangle((0, 0), 1, 1, color=protocol_colors[protocol])
        for protocol in protocols
    ]
    ax.legend(handles, protocols, title="Protocol", loc="upper right")

    plt.tight_layout()
    return fig


# Alle Diagramme erstellen und speichern
all_figures = []

for dataset_name, protocols in datasets.items():
    figures = create_chart(dataset_name, protocols, separate_mode)
    all_figures.extend(figures)

if not separate_mode:
    compression_chart = create_combined_compression_chart(datasets)
    all_figures.append(("combined_compression_ratios", compression_chart))


# Export-All-Funktion
def export_all():
    for dataset_name, fig in all_figures:
        export_path = os.path.join(output_dir, f"{dataset_name.replace('.', '_')}.png")
        fig.savefig(export_path)
        print(f"Diagramm für {dataset_name} gespeichert unter: {export_path}")
    print("Alle Diagramme erfolgreich exportiert.")


# "Export All"-Button anzeigen
export_all_button = plt.figure(figsize=(4, 1))
ax_button = export_all_button.add_axes([0.3, 0.4, 0.4, 0.3])
button = plt.Button(ax_button, "Export All")
button.on_clicked(lambda _: export_all())
plt.show()
