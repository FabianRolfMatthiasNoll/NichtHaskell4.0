import json
import pandas as pd
import matplotlib.pyplot as plt

# Load results
with open("serialization_test_results/results.json", "r") as file:
    data = json.load(file)

system_info = data[0]["system_info"]
results = pd.DataFrame(data[1:])

# Separate datasets into two groups: large and small datasets
large_datasets = results[results["Dataset"].str.contains("256MB")]
small_datasets = results[~results["Dataset"].str.contains("256MB")]


# Plot system information
def display_system_info(ax):
    sys_text = "\n".join([f"{key}: {value}" for key, value in system_info.items()])
    ax.text(
        0.1,
        0.5,
        sys_text,
        fontsize=12,
        transform=ax.transAxes,
        verticalalignment="center",
    )
    ax.set_title("System Information")
    ax.axis("off")


# Plot compression ratio
def plot_compression_ratio(ax):
    pivot_data = results.pivot(
        index="Dataset", columns="Protocol", values="Compression Ratio"
    )
    pivot_data.plot(kind="bar", ax=ax)
    ax.set_title("Compression Ratio by Protocol")
    ax.set_xlabel("Dataset")
    ax.set_ylabel("Compression Ratio")
    ax.legend(title="Protocol")
    ax.grid(axis="y")


# Plot serialization time
def plot_serialization_time(ax, dataset, title):
    pivot_data = dataset.pivot(
        index="Dataset", columns="Protocol", values="Average Serialization Time (s)"
    )
    pivot_data.plot(kind="bar", ax=ax)
    ax.set_title(title)
    ax.set_xlabel("Dataset")
    ax.set_ylabel("Serialization Time (s)")
    ax.legend(title="Protocol")
    ax.grid(axis="y")


# Plot deserialization time
def plot_deserialization_time(ax, dataset, title):
    pivot_data = dataset.pivot(
        index="Dataset", columns="Protocol", values="Average Deserialization Time (s)"
    )
    pivot_data.plot(kind="bar", ax=ax)
    ax.set_title(title)
    ax.set_xlabel("Dataset")
    ax.set_ylabel("Deserialization Time (s)")
    ax.legend(title="Protocol")
    ax.grid(axis="y")


# Create plots
fig, axes = plt.subplots(3, 2, figsize=(15, 18))
fig.suptitle("Serialization Benchmark Results", fontsize=16)

display_system_info(axes[0, 0])
plot_compression_ratio(axes[0, 1])
plot_serialization_time(
    axes[1, 0], small_datasets, "Serialization Time for Small Datasets"
)
plot_deserialization_time(
    axes[1, 1], small_datasets, "Deserialization Time for Small Datasets"
)
plot_serialization_time(
    axes[2, 0], large_datasets, "Serialization Time for Large Datasets (256MB)"
)
plot_deserialization_time(
    axes[2, 1], large_datasets, "Deserialization Time for Large Datasets (256MB)"
)

# Save and show the results
plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig("serialization_visualization_split.png")
plt.show()
