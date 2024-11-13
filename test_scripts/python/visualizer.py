import json
import pandas as pd
import matplotlib.pyplot as plt

# JSON-Ergebnisdatei laden
with open("serialization_test_results/serialization_results.json", "r") as file:
    data = json.load(file)

# Extrahiere die Ergebnisse und Systeminformationen in ein DataFrame
df = pd.DataFrame(data["results"])
system_info = data["system_info"]


# Zeichnungsfunktion für Systeminformationen
def display_system_info(ax):
    system_text = "\n".join([f"{key}: {value}" for key, value in system_info.items()])
    ax.text(
        0.02,
        0.98,
        system_text,
        ha="left",
        va="top",
        transform=ax.transAxes,
        fontsize=10,
        bbox=dict(facecolor="white", alpha=0.8),
    )
    ax.axis("off")


# Zeichnungsfunktion für Kompressionsverhältnis
def plot_compression_ratio(ax, df):
    df.pivot(index="Dataset", columns="Protocol", values="Compression Ratio").plot(
        kind="bar", ax=ax
    )
    ax.set_title("Compression Ratio by Protocol and Dataset")
    ax.set_xlabel("Dataset")
    ax.set_ylabel("Compression Ratio")
    ax.legend(title="Protocol")
    ax.grid(True)


# Zeichnungsfunktion für Serialisierungszeit
def plot_serialization_time(ax, df):
    df.pivot(index="Dataset", columns="Protocol", values="Serialization Time (s)").plot(
        kind="bar", ax=ax
    )
    ax.set_title("Serialization Time by Protocol and Dataset")
    ax.set_xlabel("Dataset")
    ax.set_ylabel("Serialization Time (s)")
    ax.legend(title="Protocol")
    ax.grid(True)


# Zeichnungsfunktion für Deserialisierungszeit
def plot_deserialization_time(ax, df):
    df.pivot(
        index="Dataset", columns="Protocol", values="Deserialization Time (s)"
    ).plot(kind="bar", ax=ax)
    ax.set_title("Deserialization Time by Protocol and Dataset")
    ax.set_xlabel("Dataset")
    ax.set_ylabel("Deserialization Time (s)")
    ax.legend(title="Protocol")
    ax.grid(True)


# Erstelle die Gesamtabbildung mit mehreren Unterplots
fig, axes = plt.subplots(2, 2, figsize=(15, 10))
fig.suptitle("Serialization Benchmark Results", fontsize=16)

# Systeminformationen, Kompressionsverhältnis, Serialisierungs- und Deserialisierungszeit darstellen
display_system_info(axes[0, 0])
plot_compression_ratio(axes[0, 1], df)
plot_serialization_time(axes[1, 0], df)
plot_deserialization_time(axes[1, 1], df)

# Diagramme anzeigen und speichern
plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig("serialization_benchmark_results.png")
plt.show()

# Speichert jede Grafik als separate PNG-Datei
fig.savefig("serialization_results_overview.png")
fig.axes[1].figure.savefig("compression_ratio_chart.png")
fig.axes[2].figure.savefig("serialization_time_chart.png")
fig.axes[3].figure.savefig("deserialization_time_chart.png")
