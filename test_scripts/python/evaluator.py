import time
import json
import os
import psutil
import platform
import datasets_pb2
import msgpack
import xml.etree.ElementTree as ET
from sys import getsizeof

# Configuration
DATASETS_DIR = "datasets"
OUTPUT_DIR = "serialization_test_results"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# System Info
def get_system_info():
    """Gather system information."""
    return {
        "CPU": platform.processor(),
        "Cores": psutil.cpu_count(logical=True),
        "Memory (GB)": round(psutil.virtual_memory().total / (1024**3), 2),
        "OS": platform.system(),
        "OS Version": platform.version(),
    }


# Measure the size of objects in memory
def get_object_size(obj):
    """Recursively calculate the in-memory size of an object."""
    size = getsizeof(obj)
    if isinstance(obj, dict):
        size += sum(get_object_size(k) + get_object_size(v) for k, v in obj.items())
    elif isinstance(obj, (list, tuple, set)):
        size += sum(get_object_size(i) for i in obj)
    return size


# Load datasets
def load_json_dataset(file_path):
    with open(file_path, "r") as f:
        return json.load(f)


# Serialization/Deserialization Functions
def serialize_json(data):
    return json.dumps(data).encode("utf-8")


def deserialize_json(data):
    return json.loads(data.decode("utf-8"))


def serialize_msgpack(data):
    return msgpack.packb(data)


def deserialize_msgpack(data):
    return msgpack.unpackb(data)


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


def deserialize_xml(data):
    root = ET.fromstring(data)
    if root.tag == "root":
        return {child.attrib.get("key", None): child.text for child in root}


def serialize_protobuf(data):
    proto_data = datasets_pb2.MixedList()
    for item in data:
        serialized_item = proto_data.items.add()
        if isinstance(item, int):
            serialized_item.int_value = item
        elif isinstance(item, float):
            serialized_item.float_value = item
        elif isinstance(item, str):
            serialized_item.string_value = item
        elif isinstance(item, dict):  # Key-value pairs
            kvpair = serialized_item.kvpair_value
            for k, v in item.items():
                kvpair.key = k
                if isinstance(v, bool):
                    kvpair.bool_value = v
                elif isinstance(v, float):
                    kvpair.double_value = v
                elif isinstance(v, str):
                    kvpair.string_value = v
        elif isinstance(item, list):  # Nested data
            nested_item = serialized_item.nested_value
            for sub_item in item:
                nested_data = nested_item.items.add()
                nested_data.items.add()
    return proto_data.SerializeToString()


def deserialize_protobuf(data):
    proto_data = datasets_pb2.MixedList()
    proto_data.ParseFromString(data)
    result = []
    for item in proto_data.items:
        if item.HasField("int_value"):
            result.append(item.int_value)
        elif item.HasField("float_value"):
            result.append(item.float_value)
        elif item.HasField("string_value"):
            result.append(item.string_value)
        elif item.HasField("kvpair_value"):
            result.append({item.kvpair_value.key: item.kvpair_value.string_value})
        elif item.HasField("nested_value"):
            result.append(
                [nested_item.items for nested_item in item.nested_value.items]
            )
    return result


# Time measurement
def measure_time(func, *args):
    start = time.perf_counter()
    result = func(*args)
    end = time.perf_counter()
    return result, end - start


# Run tests
def run_tests():
    system_info = get_system_info()
    results = []

    # Load all JSON datasets
    dataset_files = [f for f in os.listdir(DATASETS_DIR) if f.endswith(".json")]
    for dataset_file in dataset_files:
        dataset_path = os.path.join(DATASETS_DIR, dataset_file)
        dataset = load_json_dataset(dataset_path)
        in_memory_size = get_object_size(dataset)

        protocols = [
            ("JSON", serialize_json, deserialize_json, ".json"),
            ("XML", serialize_xml, deserialize_xml, ".xml"),
            ("MessagePack", serialize_msgpack, deserialize_msgpack, ".msgpack"),
            ("ProtoBuf", serialize_protobuf, deserialize_protobuf, ".pb"),
        ]

        for protocol_name, serialize_func, deserialize_func, file_ext in protocols:
            serialized_data, serialization_time = measure_time(serialize_func, dataset)
            _, deserialization_time = measure_time(deserialize_func, serialized_data)
            serialized_size = len(serialized_data)

            results.append(
                {
                    "Dataset": dataset_file,
                    "Protocol": protocol_name,
                    "Dataset In-Memory Size (bytes)": in_memory_size,
                    "Serialized Size (bytes)": serialized_size,
                    "Compression Ratio": in_memory_size / serialized_size,
                    "Serialization Time (s)": serialization_time,
                    "Deserialization Time (s)": deserialization_time,
                }
            )

    # Save results
    results_path = os.path.join(OUTPUT_DIR, "results.json")
    with open(results_path, "w") as f:
        json.dump({"system_info": system_info, "results": results}, f, indent=2)

    print(f"Results saved to {results_path}")


if __name__ == "__main__":
    run_tests()
