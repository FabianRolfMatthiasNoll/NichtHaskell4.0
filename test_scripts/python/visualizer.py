import json
import pandas as pd
import matplotlib.pyplot as plt

# Load results
with open("serialization_test_results/results.json", "r") as file:
    data = json.load(file)

results = pd.DataFrame(data["results"])
system_info = data["system_info"]


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
def plot_serialization_time(ax):
    pivot_data = results.pivot(
        index="Dataset", columns="Protocol", values="Serialization Time (s)"
    )
    pivot_data.plot(kind="bar", ax=ax)
    ax.set_title("Serialization Time by Protocol")
    ax.set_xlabel("Dataset")
    ax.set_ylabel("Time (s)")
    ax.legend(title="Protocol")
    ax.grid(axis="y")


# Plot deserialization time
def plot_deserialization_time(ax):
    pivot_data = results.pivot(
        index="Dataset", columns="Protocol", values="Deserialization Time (s)"
    )
    pivot_data.plot(kind="bar", ax=ax)
    ax.set_title("Deserialization Time by Protocol")
    ax.set_xlabel("Dataset")
    ax.set_ylabel("Time (s)")
    ax.legend(title="Protocol")
    ax.grid(axis="y")


# Plot dataset sizes
def plot_dataset_sizes(ax):
    pivot_data = results.pivot(
        index="Dataset", columns="Protocol", values="Dataset In-Memory Size (bytes)"
    )
    pivot_data.plot(kind="bar", ax=ax)
    ax.set_title("Dataset Sizes by Protocol")
    ax.set_xlabel("Dataset")
    ax.set_ylabel("Size (bytes)")
    ax.legend(title="Protocol")
    ax.grid(axis="y")


# Create plots
fig, axes = plt.subplots(3, 2, figsize=(15, 18))
fig.suptitle("Serialization Benchmark Results", fontsize=16)

display_system_info(axes[0, 0])
plot_compression_ratio(axes[0, 1])
plot_serialization_time(axes[1, 0])
plot_deserialization_time(axes[1, 1])
plot_dataset_sizes(axes[2, 0])

# Hide empty plot
axes[2, 1].axis("off")

# Save and show the results
plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig("serialization_visualization.png")
plt.show()
