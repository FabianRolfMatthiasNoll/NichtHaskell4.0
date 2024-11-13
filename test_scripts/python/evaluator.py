import time
import json
import xml.etree.ElementTree as ET
import msgpack
import psutil
import os
import random
import platform
import sys

# Setting Variables
DATASET_BATCH_SIZE = 10000

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


def approximate_deep_size(obj):
    """Estimates size of nested data without recursively measuring each entry."""
    if isinstance(obj, dict):
        key_size = sys.getsizeof(next(iter(obj.keys()), ""))  # average key size
        value_size = sys.getsizeof(next(iter(obj.values()), ""))  # average value size
        return len(obj) * (key_size + value_size)
    elif isinstance(obj, list):
        item_size = sys.getsizeof(next(iter(obj), 0))  # average item size
        return len(obj) * item_size
    return sys.getsizeof(obj)


# Optimized Data Generation for Target File Size with Batched Checking
def generate_datasets(target_size=200 * 1024**2):
    print(
        f"Generating datasets to approximately reach {target_size / (1024**2):.2f} MB..."
    )

    # Key-Value pairs generation with batch size check
    kv_pairs = {}
    print("Generating key-value pairs dataset...")
    while approximate_deep_size(kv_pairs) < target_size:
        kv_pairs.update(
            {
                f"key_{i}": f"value_{i}"
                for i in range(len(kv_pairs), len(kv_pairs) + DATASET_BATCH_SIZE)
            }
        )
    kv_size = approximate_deep_size(kv_pairs)
    print(f"Actual key-value pairs size: {kv_size / (1024 ** 2):.2f} MB")

    # Flat, Primitive List generation with batch size check
    flat_list = []
    print("Generating flat list dataset...")
    while approximate_deep_size(flat_list) < target_size:
        flat_list.extend([random.randint(1, 100) for _ in range(DATASET_BATCH_SIZE)])
    flat_list_size = approximate_deep_size(flat_list)
    print(f"Actual flat list size: {flat_list_size / (1024 ** 2):.2f} MB")

    # Composite, Complex Data Type
    complex_data = {
        "info": kv_pairs,
        "numbers": flat_list,
        "nested": [{"id": i, "name": f"name_{i}"} for i in range(1000)],
    }
    complex_data_size = approximate_deep_size(complex_data)
    print(f"Actual complex data size: {complex_data_size / (1024 ** 2):.2f} MB")

    return kv_pairs, flat_list, complex_data


# Serialization functions (without ProtoBuf)
def serialize_json(data):
    return json.dumps(data).encode("utf-8")


def serialize_xml(data):
    root = ET.Element("root")
    if isinstance(data, dict):
        for k, v in data.items():
            child = ET.SubElement(root, "item", key=k)
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
    kv_pairs, flat_list, complex_data = generate_datasets(
        target_size=1 * 1024**3
    )  # 1GB target
    datasets = {
        "kv_pairs": kv_pairs,
        "flat_list": flat_list,
        "complex_data": complex_data,
    }
    system_info = get_system_info()
    results = []

    for name, dataset in datasets.items():
        print(f"Processing dataset: {name}")
        size_in_memory = approximate_deep_size(dataset)

        protocols = [
            ("JSON", serialize_json, json.loads, ".json"),
            ("XML", serialize_xml, ET.fromstring, ".xml"),
            ("MessagePack", serialize_msgpack, msgpack.unpackb, ".msgpack"),
        ]

        for protocol_name, serializer, deserializer, file_ext in protocols:
            print(f"  Serializing with {protocol_name}...")
            serialized_data, serialization_time = measure_time(serializer, dataset)
            serialized_size = len(serialized_data)

            file_path = os.path.join(OUTPUT_DIR, f"{name}_{protocol_name}{file_ext}")
            with open(file_path, "wb") as file:
                file.write(serialized_data)
            print(
                f"    {protocol_name} serialization complete. File saved at: {file_path}"
            )

            print(f"  Deserializing {protocol_name} data...")
            _, deserialization_time = measure_time(deserializer, serialized_data)
            print(f"    {protocol_name} deserialization complete.")

            compression_ratio = size_in_memory / serialized_size

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
