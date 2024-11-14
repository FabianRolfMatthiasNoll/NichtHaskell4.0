use core::time;
use std::{collections::HashMap, io::Write, time::Instant};
use rand::Rng;
use serialize_rust::{data::SerializableData, serializer::Serializer, serializers::{json::JSONSerializer, xml::XMLSerializer}};
use std::fs::File;

pub fn generate_flat_int_list(size_in_bytes: usize) -> SerializableData {
    let mut rng = rand::thread_rng();
    SerializableData::List((0..size_in_bytes / 4).map(|_| SerializableData::Integer(rng.gen())).collect())
}

pub fn generate_flat_float_list(size_in_bytes: usize) -> SerializableData {
    let mut rng = rand::thread_rng();
    SerializableData::List((0..size_in_bytes / 4).map(|_| SerializableData::Float(rng.gen())).collect())
}

pub fn generate_flat_bigint_list(size_in_bytes: usize) -> SerializableData {
    let mut rng = rand::thread_rng();
    SerializableData::List((0..size_in_bytes / 8).map(|_| SerializableData::BigInteger(rng.gen())).collect())
}

pub fn generate_flat_bigfloat_list(size_in_bytes: usize) -> SerializableData {
    let mut rng = rand::thread_rng();
    SerializableData::List((0..size_in_bytes / 8).map(|_| SerializableData::BigFloat(rng.gen())).collect())
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

fn main() {
    let start_timestamp = Instant::now();
    let data = generate_flat_bigint_list((2 as usize).pow(30));
    let data_generated_timestamp = Instant::now();

    let serialized = JSONSerializer::serialize(&data).expect("failed to serialize");
    let data_serialized_timestamp = Instant::now();
    let compression_ratio = data.payload_size() as f32 / serialized.len() as f32;
    
    println!("took {:?} to generate data", data_generated_timestamp - start_timestamp);
    println!("took {:?} to serialize data", data_serialized_timestamp - data_generated_timestamp);
    println!("actual data size: {}", format_size(data.payload_size()));
    println!("serialized data size: {}", format_size(serialized.len()));
    println!("compression ratio: {compression_ratio}");
}
