import time
import json
import math
import os
import psutil
import platform
import datasets_pb2
import msgpack
from lxml import etree
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
    return msgpack.unpackb(data, raw=False)


def serialize_xml(data):
    def build_xml(element, data):
        if isinstance(data, dict):
            for k, v in data.items():
                child = etree.SubElement(element, "item")
                child.set("key", k)
                build_xml(child, v)
        elif isinstance(data, list):
            for item in data:
                child = etree.SubElement(element, "item")
                build_xml(child, item)
        else:
            element.text = str(data)

    root = etree.Element("root")
    build_xml(root, data)
    return etree.tostring(root, pretty_print=True)


def deserialize_xml(data):
    root = etree.fromstring(data)

    def parse_xml(element):
        if len(element):  # If element has children
            if "key" in element.attrib:
                return {element.attrib["key"]: parse_xml(element[0])}
            else:
                return [parse_xml(child) for child in element]
        else:  # Leaf node
            return element.text

    return parse_xml(root)


def serialize_protobuf(data):
    def serialize_data(data):
        proto_data = datasets_pb2.Data()
        if isinstance(data, bool):
            proto_data.boolean = data
        elif isinstance(data, int):
            if -2147483648 <= data <= 2147483647:  # 32-bit range
                proto_data.integer = data
            else:
                proto_data.big_integer = data
        elif isinstance(data, float):
            proto_data.float_value = data
        elif isinstance(data, str):
            proto_data.string_literal = data
        elif isinstance(data, dict):
            for k, v in data.items():
                kvp = proto_data.key_value_pair
                kvp.key = k
                kvp.value.CopyFrom(serialize_data(v))
        elif isinstance(data, list):
            for item in data:
                proto_data.list.elements.add().CopyFrom(serialize_data(item))
        return proto_data

    return serialize_data(data).SerializeToString()


def deserialize_protobuf(data):
    def deserialize_data(proto_data):
        if proto_data.HasField("boolean"):
            return proto_data.boolean
        elif proto_data.HasField("integer"):
            return proto_data.integer
        elif proto_data.HasField("big_integer"):
            return proto_data.big_integer
        elif proto_data.HasField("float_value"):
            return proto_data.float_value
        elif proto_data.HasField("string_literal"):
            return proto_data.string_literal
        elif proto_data.HasField("key_value_pair"):
            return {
                proto_data.key_value_pair.key: deserialize_data(
                    proto_data.key_value_pair.value
                )
            }
        elif proto_data.HasField("list"):
            return [deserialize_data(element) for element in proto_data.list.elements]
        return None

    proto_data = datasets_pb2.Data()
    proto_data.ParseFromString(data)
    return deserialize_data(proto_data)


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
    print(f"Found {len(dataset_files)} Datasets...")
    for dataset_file in dataset_files:
        dataset_path = os.path.join(DATASETS_DIR, dataset_file)
        print(f"Loading {dataset_file}...")
        dataset = load_json_dataset(dataset_path)
        in_memory_size = get_object_size(dataset)
        print(f"Loaded with {in_memory_size / math.pow(1024, 2)} MB")

        protocols = [
            ("JSON", serialize_json, deserialize_json, ".json"),
            ("XML", serialize_xml, deserialize_xml, ".xml"),
            ("MessagePack", serialize_msgpack, deserialize_msgpack, ".msgpack"),
            ("ProtoBuf", serialize_protobuf, deserialize_protobuf, ".pb"),
        ]

        for protocol_name, serialize_func, deserialize_func, file_ext in protocols:
            print(f"Meassuring Performance of {protocol_name}...")
            print("Serializing...")
            serialized_data, serialization_time = measure_time(serialize_func, dataset)
            print("Deserializing...")
            _, deserialization_time = measure_time(deserialize_func, serialized_data)
            serialized_size = len(serialized_data)
            compression_ratio = in_memory_size / serialized_size

            results.append(
                {
                    "Dataset": dataset_file,
                    "Protocol": protocol_name,
                    "Dataset In-Memory Size (bytes)": in_memory_size,
                    "Serialized Size (bytes)": serialized_size,
                    "Compression Ratio": compression_ratio,
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
