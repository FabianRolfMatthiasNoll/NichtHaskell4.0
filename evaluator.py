import time
import json
import xml.etree.ElementTree as ET
import msgpack
import psutil
import os
import random
import pickle
import platform

from tqdm import tqdm

# Setup paths
OUTPUT_DIR = "serialization_test_results"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# Hardware and System Information
def get_system_info():
    print("Collecting system information...")
    info = {
        "machine": platform.machine(),
        "processor": platform.processor(),
        "system": platform.system(),
        "release": platform.release(),
        "python_version": platform.python_version(),
        "memory": f"{psutil.virtual_memory().total / (1024 ** 3):.2f} GB",
        "cpu_freq": psutil.cpu_freq().current if psutil.cpu_freq() else None,
        "cpu_cores": psutil.cpu_count(logical=False),
    }
    print("System information collected.\n")
    return info


# Adjusted Data Generation for ~200 MB per dataset and Progress Bars
def generate_datasets():
    print("Generating datasets of approximately 200 MB each...")

    # Target approximate size in bytes (200 MB)
    target_size = 200 * 1024**2

    # Key-Value pairs - Reduce to ~200 MB
    kv_target_count = target_size // 100  # Approximate size per entry
    print("Generating key-value pairs dataset...")
    kv_pairs = {
        f"key_{i}": f"value_{i}"
        for i in tqdm(range(kv_target_count), desc="Key-Value Pairs")
    }
    kv_size = len(pickle.dumps(kv_pairs))
    print(f"Actual key-value pairs size in memory: {kv_size / (1024 ** 2):.2f} MB")

    # Flat, Primitive List - Reduce to ~200 MB
    flat_list_target_count = target_size // 4  # Approximate size per integer
    print("Generating flat list dataset...")
    flat_list = [
        random.randint(1, 100)
        for _ in tqdm(range(flat_list_target_count), desc="Flat List")
    ]
    flat_list_size = len(pickle.dumps(flat_list))
    print(f"Actual flat list size in memory: {flat_list_size / (1024 ** 2):.2f} MB")

    # Composite, Complex Datatype with Reduced Nested Structure
    complex_data = {
        "info": kv_pairs,
        "numbers": flat_list,
        "nested": [
            {"id": i, "name": f"name_{i}"} for i in range(100)
        ],  # Smaller nested count for testing
    }
    complex_data_size = len(pickle.dumps(complex_data))
    print(
        f"Actual complex data size in memory: {complex_data_size / (1024 ** 2):.2f} MB"
    )

    print("All datasets generated and size verified.\n")
    return kv_pairs, flat_list, complex_data


# Serialization functions (without ProtoBuf)
def serialize_json(data):
    return json.dumps(data).encode("utf-8")


def serialize_xml(data):
    root = ET.Element("root")
    if isinstance(data, dict):
        for k, v in data.items():
            child = ET.SubElement(root, k)
            child.text = str(v)
    elif isinstance(data, list):
        for item in data:
            child = ET.SubElement(root, "item")
            child.text = str(item)
    return ET.tostring(root, encoding="utf-8")


def serialize_msgpack(data):
    return msgpack.packb(data)


# Time Measurement Wrapper
def measure_time(func, *args):
    start = time.perf_counter()
    result = func(*args)
    end = time.perf_counter()
    return result, end - start


# Main Test Function with All Formats
def run_tests():
    kv_pairs, flat_list, complex_data = generate_datasets()

    datasets = {
        "kv_pairs": kv_pairs,
        "flat_list": flat_list,
        "complex_data": complex_data,
    }

    system_info = get_system_info()
    results = []

    for name, dataset in datasets.items():
        print(f"Processing dataset: {name}")

        # In-memory size
        size_in_memory = len(pickle.dumps(dataset))

        # Apply all serialization formats to each dataset
        protocols = [
            ("JSON", serialize_json, json.loads, ".json"),
            ("XML", serialize_xml, ET.fromstring, ".xml"),
            ("MessagePack", serialize_msgpack, msgpack.unpackb, ".msgpack"),
        ]

        for protocol_name, serializer, deserializer, file_ext in protocols:
            print(f"  Serializing with {protocol_name}...")
            # Serialization
            serialized_data, serialization_time = measure_time(serializer, dataset)
            serialized_size = len(serialized_data)

            # Save file with the correct extension
            file_path = os.path.join(OUTPUT_DIR, f"{name}_{protocol_name}{file_ext}")
            with open(file_path, "wb") as file:
                file.write(serialized_data)
            print(
                f"    {protocol_name} serialization complete. File saved at: {file_path}"
            )

            # Deserialization
            print(f"  Deserializing {protocol_name} data...")
            _, deserialization_time = measure_time(deserializer, serialized_data)
            print(f"    {protocol_name} deserialization complete.")

            # Compression Ratio
            compression_ratio = size_in_memory / serialized_size

            # Record Results
            results.append(
                {
                    "Dataset": name,
                    "Protocol": protocol_name,
                    "Size In Memory (bytes)": size_in_memory,
                    "Serialized Size (bytes)": serialized_size,
                    "Compression Ratio": compression_ratio,
                    "Serialization Time (s)": serialization_time,
                    "Deserialization Time (s)": deserialization_time,
                    "File Path": file_path,
                }
            )

        print(f"Finished processing dataset: {name}\n")

    print("All datasets processed. Writing results to JSON file...\n")
    return {"system_info": system_info, "results": results}


# Run the tests
output = run_tests()

# Save results to a file
results_file = os.path.join(OUTPUT_DIR, "serialization_results.json")
with open(results_file, "w") as f:
    json.dump(output, f, indent=2)

print(f"Results saved to {results_file}\n")
print("Script execution complete.")
