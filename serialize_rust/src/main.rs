use core::time;
use std::{collections::HashMap, fs, hash::Hash, io::Write, time::Instant};
use rand::Rng;
use serde::{Deserialize, Serialize};
use sysinfo::System;
use serde_protobuf::value::Message;
use serialize_rust::{data::SerializableData, datagen::{list, random_bigfloat, random_bigint, random_boolean, random_choice, random_float, random_int, random_kvpair, random_list, random_string}, serializer::Serializer, serializers::{json::JSONSerializer, messagepack::MessagepackSerializer, protobuf::ProtobufSerializer, xml::XMLSerializer}};

const DATASET_DIR: &str = "../datasets";

#[derive(Serialize, Deserialize)]
pub struct SysInfo {
    #[serde(rename = "CPU")]
    pub cpu: String,
    #[serde(rename = "Cores")]
    pub cores: u32,
    #[serde(rename = "Memory (GB)")]
    pub memory: f64,
    #[serde(rename = "OS")]
    pub os: String
}

#[derive(Serialize, Deserialize)]
pub struct SysInfoWrapper {
    pub system_info: SysInfo
}

#[derive(Serialize, Deserialize, Default, Clone)]
struct DatasetResult {
    #[serde(rename = "Dataset")]
    pub dataset: String,
    #[serde(rename = "Protocol")]
    pub protocol: String,
    #[serde(rename = "Dataset In-Memory Size (bytes)")]
    pub datasize_memory: u64,
    #[serde(rename = "Average Serialized Size (bytes)")]
    pub datasize_serialized: Option<u64>,
    #[serde(rename = "Compression Ratio")]
    pub compression_ratio: Option<f64>,
    #[serde(rename = "Average Serialization Time (s)")]
    pub serialization_time: Option<f64>,
    #[serde(rename = "Average Deserialization Time (s)")]
    pub deserialization_time: Option<f64>,
}

#[derive(Serialize, Deserialize)]
#[serde(untagged)]
pub enum ResultData {
    SystemInfo(SysInfoWrapper),
    ResultSet(DatasetResult),
}

fn format_size(bytes: usize) -> String {
    const KB: usize = 1024;
    const MB: usize = KB * 1024;
    const GB: usize = MB * 1024;
    const TB: usize = GB * 1024;

    if bytes >= TB {
        format!("{:.2} TB", bytes as f64 / TB as f64)
    } else if bytes >= GB {
        format!("{:.2} GB", bytes as f64 / GB as f64)
    } else if bytes >= MB {
        format!("{:.2} MB", bytes as f64 / MB as f64)
    } else if bytes >= KB {
        format!("{:.2} KB", bytes as f64 / KB as f64)
    } else {
        format!("{} bytes", bytes)
    }
}

fn generate_dataset_flat_intlist(size_in_bytes: usize) -> SerializableData {
    random_list(size_in_bytes / 4, random_int)
}

fn generate_dataset_deep_flat_intlist(depth: usize, size_in_bytes: usize) -> SerializableData {
    if depth == 0 {
        generate_dataset_flat_intlist(size_in_bytes)
    } else {
        SerializableData::KeyValuePair(String::from("child"), Box::new(generate_dataset_deep_flat_intlist(depth - 1, size_in_bytes)))
    }
}

fn generate_dataset_flat_floatlist(size_in_bytes: usize) -> SerializableData {
    random_list(size_in_bytes / 4, random_float)
}

fn generate_dataset_deep_flat_floatlist(depth: usize, size_in_bytes: usize) -> SerializableData {
    if depth == 0 {
        generate_dataset_flat_floatlist(size_in_bytes)
    } else {
        SerializableData::KeyValuePair(String::from("child"), Box::new(generate_dataset_deep_flat_floatlist(depth - 1, size_in_bytes)))
    }
}

fn generate_dataset_int_tree(depth: usize, children_per_node: usize) -> SerializableData {
    if depth <= 0 {
        SerializableData::List(vec![
            SerializableData::KeyValuePair(String::from("data"), Box::new(random_int())),
            SerializableData::KeyValuePair(String::from("children"), Box::new(SerializableData::List(Vec::new())))
        ])
    } else {
        SerializableData::List(vec![
            SerializableData::KeyValuePair(String::from("data"), Box::new(random_int())),
            SerializableData::KeyValuePair(String::from("children"), Box::new(random_list(children_per_node, || generate_dataset_int_tree(depth - 1, children_per_node)))),
        ])
    }
}

fn generate_datasets() {
    let dataset = generate_dataset_flat_intlist((2 as usize).pow(28));
    let serialized = JSONSerializer::serialize(&dataset).unwrap();
    std::fs::write(format!("{}/dataset_flat_intlist_256MB.json", DATASET_DIR), &serialized).unwrap();
    drop(dataset);
    drop(serialized);

    let dataset = generate_dataset_flat_intlist((2 as usize).pow(23));
    let serialized = JSONSerializer::serialize(&dataset).unwrap();
    std::fs::write(format!("{}/dataset_flat_intlist_8MB.json", DATASET_DIR), &serialized).unwrap();
    drop(dataset);
    drop(serialized);

    let dataset = generate_dataset_deep_flat_intlist(10000, (2 as usize).pow(28));
    let serialized = JSONSerializer::serialize(&dataset).unwrap();
    std::fs::write(format!("{}/dataset_deep_flat_intlist_256MB.json", DATASET_DIR), &serialized).unwrap();
    drop(dataset);
    drop(serialized);

    let dataset = generate_dataset_deep_flat_intlist(50, (2 as usize).pow(28));
    let serialized = JSONSerializer::serialize(&dataset).unwrap();
    std::fs::write(format!("{}/dataset_not_so_deep_flat_intlist_256MB.json", DATASET_DIR), &serialized).unwrap();
    drop(dataset);
    drop(serialized);

    let dataset = generate_dataset_deep_flat_intlist(10000, (2 as usize).pow(23));
    let serialized = JSONSerializer::serialize(&dataset).unwrap();
    std::fs::write(format!("{}/dataset_deep_flat_intlist_8MB.json", DATASET_DIR), &serialized).unwrap();
    drop(dataset);
    drop(serialized);

    let dataset = generate_dataset_deep_flat_intlist(50, (2 as usize).pow(23));
    let serialized = JSONSerializer::serialize(&dataset).unwrap();
    std::fs::write(format!("{}/dataset_not_so_deep_flat_intlist_8MB.json", DATASET_DIR), &serialized).unwrap();
    drop(dataset);
    drop(serialized);

    let dataset = generate_dataset_flat_floatlist((2 as usize).pow(28));
    let serialized = JSONSerializer::serialize(&dataset).unwrap();
    std::fs::write(format!("{}/dataset_flat_floatlist_256MB.json", DATASET_DIR), &serialized).unwrap();
    drop(dataset);
    drop(serialized);

    let dataset = generate_dataset_flat_floatlist((2 as usize).pow(23));
    let serialized = JSONSerializer::serialize(&dataset).unwrap();
    std::fs::write(format!("{}/dataset_flat_floatlist_8MB.json", DATASET_DIR), &serialized).unwrap();
    drop(dataset);
    drop(serialized);

    let dataset = generate_dataset_deep_flat_floatlist(10000, (2 as usize).pow(28));
    let serialized = JSONSerializer::serialize(&dataset).unwrap();
    std::fs::write(format!("{}/dataset_deep_flat_floatlist_256MB.json", DATASET_DIR), &serialized).unwrap();
    drop(dataset);
    drop(serialized);

    let dataset = generate_dataset_deep_flat_floatlist(50, (2 as usize).pow(28));
    let serialized = JSONSerializer::serialize(&dataset).unwrap();
    std::fs::write(format!("{}/dataset_not_so_deep_flat_floatlist_256MB.json", DATASET_DIR), &serialized).unwrap();
    drop(dataset);
    drop(serialized);

    let dataset = generate_dataset_deep_flat_floatlist(10000, (2 as usize).pow(23));
    let serialized = JSONSerializer::serialize(&dataset).unwrap();
    std::fs::write(format!("{}/dataset_deep_flat_floatlist_8MB.json", DATASET_DIR), &serialized).unwrap();
    drop(dataset);
    drop(serialized);

    let dataset = generate_dataset_deep_flat_floatlist(50, (2 as usize).pow(23));
    let serialized = JSONSerializer::serialize(&dataset).unwrap();
    std::fs::write(format!("{}/dataset_not_so_deep_flat_floatlist_8MB.json", DATASET_DIR), &serialized).unwrap();
    drop(dataset);
    drop(serialized);

    let dataset = generate_dataset_int_tree(4, 8);
    let serialized = JSONSerializer::serialize(&dataset).unwrap();
    std::fs::write(format!("{}/dataset_int_tree_small.json", DATASET_DIR), &serialized).unwrap();
    drop(dataset);
    drop(serialized);

    let dataset = generate_dataset_int_tree(8, 8);
    let serialized = JSONSerializer::serialize(&dataset).unwrap();
    std::fs::write(format!("{}/dataset_int_tree_large.json", DATASET_DIR), &serialized).unwrap();
    drop(dataset);
    drop(serialized);
}

fn fetch_sysinfo() -> SysInfo {
    let mut system = System::new_all();
    system.refresh_all();

    // Get CPU name and number of cores
    let cpu_name = system.cpus().first().map(|cpu| cpu.brand()).unwrap_or("Unknown CPU").to_string();
    let cpu_cores = system.physical_core_count().unwrap_or(0) as u32;
    let total_memory = ((system.total_memory() as f64 / 1024f64.powf(3.0) * 100.0).round() / 100.0);
    let os_type = System::name().unwrap_or_else(|| "Unknown OS".to_string());

    SysInfo {
        cpu: cpu_name,
        cores: cpu_cores,
        memory: total_memory,
        os: os_type,
    }
}

fn evaluate_dataset(file: &str) -> Result<Vec<DatasetResult>, String> {
    type NamedSerializer = (&'static str, fn (&SerializableData) -> Result<Vec<u8>, String>, fn (&Vec<u8>) -> Result<SerializableData, String>);
    let serializers: Vec<NamedSerializer> = vec![
        ("JSON",        JSONSerializer::serialize, JSONSerializer::deserialize),
        ("XML",         XMLSerializer::serialize, XMLSerializer::deserialize),
        ("Protobuf",    ProtobufSerializer::serialize, ProtobufSerializer::deserialize),
        ("Messagepack", MessagepackSerializer::serialize, MessagepackSerializer::deserialize),
    ];

    let mut results = vec![DatasetResult::default(); 4];
    let data = std::fs::read(format!("{}/{}", DATASET_DIR, file)).map_err(|err| err.to_string())?;
    let data = JSONSerializer::deserialize(&data)?;

    for (index, (name, serializer, deserializer)) in serializers.iter().enumerate() {

        results[index].dataset = String::from(file);
        results[index].protocol = String::from(*name);
        results[index].datasize_memory = data.memory_size() as u64;

        let start_timestamp = Instant::now();
        if let Ok(serialized_data) = serializer(&data) {
            let end_timestamp = Instant::now();
            let serialize_time = end_timestamp - start_timestamp;
            let compression_ratio = data.payload_size() as f32 / serialized_data.len() as f32;

            results[index].compression_ratio = Some(compression_ratio as f64);
            results[index].datasize_serialized = Some(serialized_data.len() as u64);
            results[index].serialization_time = Some(serialize_time.as_secs_f64());

            let start_timestamp = Instant::now();
            if let Ok(_) = deserializer(&serialized_data) {
                let end_timestamp = Instant::now();
                let deserialize_time = end_timestamp - start_timestamp;

                results[index].deserialization_time = Some(deserialize_time.as_secs_f64());
            }
        }
    }

    Ok(results)
}

fn main() {
    //generate_datasets();

    let mut results: Vec<DatasetResult> = Vec::new();

    for entry in std::fs::read_dir(DATASET_DIR).unwrap() {
        if let Ok(file) = entry {
            let filename = String::from(file.file_name().to_str().unwrap());
            if file.file_type().unwrap().is_file() {
                if let Ok(res) = evaluate_dataset(&filename) {
                    results.extend(res);
                }
            }

            if filename == "dataset_int_tree_small.json" {
                break;
            }
        }
    }

    let mut total_result = vec![
        ResultData::SystemInfo(SysInfoWrapper { systeminfo: fetch_sysinfo() }),
    ];

    total_result.extend(results.iter().map(|result| ResultData::ResultSet(result.clone())));
    println!("{}", serde_json::to_string_pretty(&total_result).unwrap());
}
