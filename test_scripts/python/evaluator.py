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
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "results.json")
XML_THRESHOLD_MB = 100
REPEATS = 10  # Number of repetitions per test
os.makedirs(OUTPUT_DIR, exist_ok=True)


# System Info
def get_system_info():
    """Gather system information."""
    return {
        "CPU": platform.processor(),
        "Cores": psutil.cpu_count(logical=True),
        "Memory (GB)": round(psutil.virtual_memory().total / (1024**3), 2),
        "OS": platform.system(),
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


def serialize_xml(data, output_file=None):
    """
    Serialize data to XML.
    For large datasets (above threshold), use streaming to minimize memory usage.
    """

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

    if output_file:  # Streaming approach
        with open(output_file, "wb") as f:
            tree = etree.ElementTree(root)
            tree.write(f, pretty_print=True, xml_declaration=True, encoding="utf-8")
        return None  # No data returned for streaming
    else:  # In-memory approach
        return etree.tostring(
            root, pretty_print=True, xml_declaration=True, encoding="utf-8"
        )


def deserialize_xml(input_file=None, xml_data=None):
    """
    Deserialize XML data.
    If input_file is provided, use streaming; otherwise, deserialize from memory.
    """

    def parse_element(element):
        if len(element):  # Element has children
            if "key" in element.attrib:
                return {element.attrib["key"]: parse_element(list(element)[0])}
            else:
                return [parse_element(child) for child in element]
        else:  # Leaf node
            return element.text

    if input_file:  # Streaming approach
        data = []
        for _, element in etree.iterparse(input_file, tag="item"):
            data.append(parse_element(element))
            element.clear()  # Free memory for processed elements
        return data
    else:  # In-memory approach
        root = etree.fromstring(xml_data)
        return parse_element(root)


def serialize_flat_int_list(data):
    proto_data = datasets_pb2.FlatIntList()
    proto_data.values.extend(data)
    return proto_data.SerializeToString()


def deserialize_flat_int_list(data):
    proto_data = datasets_pb2.FlatIntList()
    proto_data.ParseFromString(data)
    return list(proto_data.values)


def serialize_deep_flat_int_list(data):
    def build_node(data, node):
        if isinstance(data.get("child"), list):  # Terminal node
            # Populate the `value_list` field
            value_list = node.value_list
            value_list.values.extend(data["child"])
        elif "child" in data and isinstance(data["child"], dict):  # Intermediate node
            # Populate the `child` field
            build_node(data["child"], node.child)
        else:
            raise ValueError(f"Invalid structure at this level:")

    proto_data = datasets_pb2.DeepFlatIntList()
    build_node(data, proto_data.root)
    return proto_data.SerializeToString()


def deserialize_deep_flat_int_list(data):
    def parse_node(node):
        if node.HasField("value_list"):  # Terminal node with values
            return {"child": list(node.value_list.values)}
        elif node.HasField("child"):  # Intermediate node
            return {"child": parse_node(node.child)}
        else:
            raise ValueError(
                "Invalid Protobuf structure: both `child` and `value_list` are unset"
            )

    proto_data = datasets_pb2.DeepFlatIntList()
    proto_data.ParseFromString(data)
    return parse_node(proto_data.root)


def serialize_deep_flat_float_list(data):
    def build_node(data, node):
        if isinstance(data.get("child"), list):  # Terminal node
            # Populate the `value_list` field
            value_list = node.value_list
            value_list.values.extend(data["child"])
        elif "child" in data and isinstance(data["child"], dict):  # Intermediate node
            # Populate the `child` field
            build_node(data["child"], node.child)
        else:
            raise ValueError(f"Invalid structure at this level:")

    proto_data = datasets_pb2.DeepFlatFloatList()
    build_node(data, proto_data.root)
    return proto_data.SerializeToString()


def deserialize_deep_flat_float_list(data):
    def parse_node(node):
        if node.HasField("value_list"):  # Terminal node with values
            return {"child": list(node.value_list.values)}
        elif node.HasField("child"):  # Intermediate node
            return {"child": parse_node(node.child)}
        else:
            raise ValueError(
                "Invalid Protobuf structure: both `child` and `value_list` are unset"
            )

    proto_data = datasets_pb2.DeepFlatFloatList()
    proto_data.ParseFromString(data)
    return parse_node(proto_data.root)


def serialize_flat_float_list(data):
    proto_data = datasets_pb2.FlatFloatList()
    proto_data.values.extend(data)
    return proto_data.SerializeToString()


def deserialize_flat_float_list(data):
    proto_data = datasets_pb2.FlatFloatList()
    proto_data.ParseFromString(data)
    return list(proto_data.values)


def serialize_int_tree(data):
    def build_tree(data, node):
        node.data = data[0]["data"]
        for child in data[1]["children"]:
            child_node = node.children.add()
            build_tree(child, child_node)

    proto_data = datasets_pb2.IntTree()
    build_tree(data, proto_data.root)
    return proto_data.SerializeToString()


def deserialize_int_tree(data):
    def parse_tree(node):
        return {
            "data": node.data,
            "children": [parse_tree(child) for child in node.children],
        }

    proto_data = datasets_pb2.IntTree()
    proto_data.ParseFromString(data)
    return parse_tree(proto_data.root)


# Time measurement
def measure_time(func, *args):
    start = time.perf_counter()
    result = func(*args)
    end = time.perf_counter()
    return result, end - start


# Append results to file
def append_to_file(filepath, data):
    with open(filepath, "a") as f:
        f.write(json.dumps(data, indent=2) + "\n")


def run_tests():
    # Write system info at the beginning
    system_info = get_system_info()
    with open(OUTPUT_FILE, "w") as f:
        f.write(json.dumps({"system_info": system_info}, indent=2) + "\n")

    # Load all JSON datasets
    dataset_files = [f for f in os.listdir(DATASETS_DIR) if f.endswith(".json")]
    file_amount = len(dataset_files)
    print(f"Found {file_amount} Datasets...")

    for i, dataset_file in enumerate(dataset_files):
        dataset_path = os.path.join(DATASETS_DIR, dataset_file)
        print(f"[{i+1}|{file_amount}]Loading {dataset_file}")
        dataset = load_json_dataset(dataset_path)
        in_memory_size = get_object_size(dataset)
        dataset_size_mb = in_memory_size / math.pow(1024, 2)
        print(f"Loaded with {dataset_size_mb:.2f} MB")

        # Assign Protobuf functions based on dataset type
        if "deep_flat_intlist" in dataset_file:
            serialize_func, deserialize_func = (
                serialize_deep_flat_int_list,
                deserialize_deep_flat_int_list,
            )
        elif "flat_intlist" in dataset_file:
            serialize_func, deserialize_func = (
                serialize_flat_int_list,
                deserialize_flat_int_list,
            )
        elif "deep_flat_floatlist" in dataset_file:
            serialize_func, deserialize_func = (
                serialize_deep_flat_float_list,
                deserialize_deep_flat_float_list,
            )
        elif "flat_floatlist" in dataset_file:
            serialize_func, deserialize_func = (
                serialize_flat_float_list,
                deserialize_flat_float_list,
            )
        elif "int_tree" in dataset_file:
            serialize_func, deserialize_func = serialize_int_tree, deserialize_int_tree
        else:
            continue

        protocols = [
            ("JSON", serialize_json, deserialize_json),
            (
                "XML",
                lambda data: serialize_xml(
                    data,
                    (
                        f"{OUTPUT_DIR}/temp.xml"
                        if dataset_size_mb > XML_THRESHOLD_MB
                        else None
                    ),
                ),
                lambda data: deserialize_xml(
                    input_file=(
                        f"{OUTPUT_DIR}/temp.xml"
                        if dataset_size_mb > XML_THRESHOLD_MB
                        else None
                    ),
                    xml_data=data if dataset_size_mb <= XML_THRESHOLD_MB else None,
                ),
            ),
            ("MessagePack", serialize_msgpack, deserialize_msgpack),
            ("ProtoBuf", serialize_func, deserialize_func),
        ]

        for protocol_name, serialize_func, deserialize_func in protocols:
            print(f"Testing {protocol_name}...")
            serialization_times = []
            deserialization_times = []
            sizes = []

            for i in range(REPEATS):
                print(f"[{i+1}|{REPEATS}] Serialisation")
                # Measure serialization
                serialized_data, serialization_time = measure_time(
                    serialize_func, dataset
                )
                serialization_times.append(serialization_time)

                print(f"[{i+1}|{REPEATS}] Deserialisation")
                # Measure deserialization
                _, deserialization_time = measure_time(
                    deserialize_func, serialized_data
                )
                deserialization_times.append(deserialization_time)

                # Measure size
                if protocol_name == "XML" and dataset_size_mb > XML_THRESHOLD_MB:
                    sizes.append(os.path.getsize(f"{OUTPUT_DIR}/temp.xml"))
                else:
                    sizes.append(len(serialized_data))

            # Calculate averages
            avg_serialization_time = sum(serialization_times) / REPEATS
            avg_deserialization_time = sum(deserialization_times) / REPEATS
            avg_size = sum(sizes) / REPEATS
            compression_ratio = in_memory_size / avg_size

            # Append results
            result = {
                "Dataset": dataset_file,
                "Protocol": protocol_name,
                "Dataset In-Memory Size (bytes)": in_memory_size,
                "Average Serialized Size (bytes)": avg_size,
                "Compression Ratio": compression_ratio,
                "Average Serialization Time (s)": avg_serialization_time,
                "Average Deserialization Time (s)": avg_deserialization_time,
            }
            append_to_file(OUTPUT_FILE, result)
            print(f"Result appended for {protocol_name}")

    print(f"All results saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    run_tests()
