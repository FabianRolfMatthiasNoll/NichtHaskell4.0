use core::time;
use std::{collections::HashMap, fs, io::Write, time::Instant};
use rand::Rng;
use serialize_rust::{data::SerializableData, datagen::{random_bigfloat, random_bigint, random_boolean, random_choice, random_float, random_int, random_kvpair, random_list, random_string}, serializer::Serializer, serializers::{json::JSONSerializer, protobuf::ProtobufSerializer, xml::XMLSerializer}};
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

    // "generate a list with 40 entries, each entry being either:
    // - a random i32
    // - a random float
    // - a random string of length 3
    // - a random kvpair, with a key length of 5 and the value being either:
    //     - a random boolean
    //     - a random f64
    // "
    // This is just an example, but you get the gist.
    // We can declaratively build a pretty complex dataset, but with runtime parametrisation. Neat.
    let data = random_list(4000, || random_choice(vec![
        random_int,
        random_float,
        || random_string(3),
        || random_kvpair(5, || random_choice(vec![
            random_boolean,
            random_bigfloat
        ]))
    ]));
    let data_generated_timestamp = Instant::now();

    let serialized = ProtobufSerializer::serialize(&data).expect("failed to serialize");
    let data_serialized_timestamp = Instant::now();
    let compression_ratio = data.payload_size() as f32 / serialized.len() as f32;
    
    println!("took {:?} to generate data", data_generated_timestamp - start_timestamp);
    println!("took {:?} to serialize data", data_serialized_timestamp - data_generated_timestamp);
    println!("actual data size: {}", format_size(data.payload_size()));
    println!("serialized data size: {}", format_size(serialized.len()));
    println!("compression ratio: {compression_ratio}");
}
