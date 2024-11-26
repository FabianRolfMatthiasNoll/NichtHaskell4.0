use core::time;
use std::{collections::HashMap, fs, io::Write, time::Instant};
use rand::Rng;
use serde_protobuf::value::Message;
use serialize_rust::{data::SerializableData, datagen::{list, random_bigfloat, random_bigint, random_boolean, random_choice, random_float, random_int, random_kvpair, random_list, random_string}, serializer::Serializer, serializers::{json::JSONSerializer, messagepack::MessagepackSerializer, protobuf::ProtobufSerializer, xml::XMLSerializer}};

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
    std::fs::write("../datasets/dataset_flat_intlist_256MB.json", &serialized).unwrap();

    let dataset = generate_dataset_flat_intlist((2 as usize).pow(23));
    let serialized = JSONSerializer::serialize(&dataset).unwrap();
    std::fs::write("../datasets/dataset_flat_intlist_8MB.json", &serialized).unwrap();

    let dataset = generate_dataset_deep_flat_intlist(10000, (2 as usize).pow(28));
    let serialized = JSONSerializer::serialize(&dataset).unwrap();
    std::fs::write("../datasets/dataset_deep_flat_intlist_256MB.json", &serialized).unwrap();

    let dataset = generate_dataset_deep_flat_intlist(10000, (2 as usize).pow(23));
    let serialized = JSONSerializer::serialize(&dataset).unwrap();
    std::fs::write("../datasets/dataset_deep_flat_intlist_8MB.json", &serialized).unwrap();

    let dataset = generate_dataset_flat_floatlist((2 as usize).pow(28));
    let serialized = JSONSerializer::serialize(&dataset).unwrap();
    std::fs::write("../datasets/dataset_flat_floatlist_256MB.json", &serialized).unwrap();

    let dataset = generate_dataset_flat_floatlist((2 as usize).pow(23));
    let serialized = JSONSerializer::serialize(&dataset).unwrap();
    std::fs::write("../datasets/dataset_flat_floatlist_8MB.json", &serialized).unwrap();

    let dataset = generate_dataset_deep_flat_floatlist(10000, (2 as usize).pow(28));
    let serialized = JSONSerializer::serialize(&dataset).unwrap();
    std::fs::write("../datasets/dataset_deep_flat_floatlist_256MB.json", &serialized).unwrap();

    let dataset = generate_dataset_deep_flat_floatlist(10000, (2 as usize).pow(23));
    let serialized = JSONSerializer::serialize(&dataset).unwrap();
    std::fs::write("../datasets/dataset_deep_flat_floatlist_8MB.json", &serialized).unwrap();

    let dataset = generate_dataset_int_tree(4, 8);
    let serialized = JSONSerializer::serialize(&dataset).unwrap();
    std::fs::write("../datasets/dataset_int_tree_small.json", &serialized).unwrap();

    let dataset = generate_dataset_int_tree(8, 8);
    let serialized = JSONSerializer::serialize(&dataset).unwrap();
    std::fs::write("../datasets/dataset_int_tree_large.json", &serialized).unwrap();

}

fn main() {

    generate_datasets();
    return;

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
    let data = random_list(400000, || random_choice(vec![
        random_int,
        random_float,
        || random_string(3),
        || random_kvpair(5, || random_choice(vec![
            random_boolean,
            random_bigfloat
        ]))
    ]));

    type NamedSerializer = (&'static str, fn (&SerializableData) -> Result<Vec<u8>, String>);
    let serializers: Vec<NamedSerializer> = vec![
        ("Protobuf",    ProtobufSerializer::serialize),
        ("Messagepack", MessagepackSerializer::serialize),
        ("XML",         XMLSerializer::serialize),
        ("JSON",        JSONSerializer::serialize)
    ];

    for (name, serializer) in serializers {
        let start_timestamp = Instant::now();
        let serialized_data = serializer(&data).expect("failed to serialize");
        let end_timestamp = Instant::now();
        let time_taken = end_timestamp - start_timestamp;
        let compression_ratio = data.payload_size() as f32 / serialized_data.len() as f32;

        println!("Serializer '{name}':");
        println!("took {:?} to serialize data", time_taken);
        println!("actual data size: {}", format_size(data.payload_size()));
        println!("serialized data size: {}", format_size(serialized_data.len()));
        println!("compression ratio: {compression_ratio}");
        println!("");
    }
}
