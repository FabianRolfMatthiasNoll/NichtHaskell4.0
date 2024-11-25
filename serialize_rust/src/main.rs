use std::{env, fs::File, io::BufWriter};
use serde_json::to_writer;
use serialize_rust::{
    data::SerializableData,
    datagen::{random_choice, random_float, random_int, random_kvpair, random_list, random_string, random_boolean, random_bigfloat},
};

fn main() -> std::io::Result<()> {
    let args: Vec<String> = env::args().collect();
    let size_in_bytes = args.get(1)
        .and_then(|s| s.parse::<usize>().ok())
        .unwrap_or(1024 * 1024 * 1024); // Default to 1GB if no size is provided

    // Generate datasets
    let mixed_dataset = generate_mixed_dataset(size_in_bytes / 3);
    let nested_dataset = generate_nested_dataset(size_in_bytes / 3, 5, 10);
    let kv_pairs_dataset = generate_kv_dataset(size_in_bytes / 3, 10);

    // Save datasets
    save_dataset("datasets/mixed_dataset.json", mixed_dataset)?;
    save_dataset("datasets/nested_dataset.json", nested_dataset)?;
    save_dataset("datasets/kv_pairs_dataset.json", kv_pairs_dataset)?;

    Ok(())
}

fn save_dataset(file_name: &str, dataset: SerializableData) -> std::io::Result<()> {
    let file = File::create(file_name)?;
    let writer = BufWriter::new(file);
    to_writer(writer, &dataset).expect("Failed to serialize dataset to JSON");
    println!("Generated and saved dataset: {}", file_name);
    Ok(())
}

fn generate_mixed_dataset(size: usize) -> SerializableData {
    random_list(size / 100, || {
        random_choice(vec![
            random_int,
            random_float,
            || random_string(10),
            || random_kvpair(10, random_boolean),
        ])
    })
}

fn generate_nested_dataset(size: usize, depth: usize, breadth: usize) -> SerializableData {
    if size <= 0 || depth == 0 {
        random_choice(vec![
            random_int,
            random_float,
            || random_string(10),
            || random_boolean(),
            || random_kvpair(5, random_bigfloat),
        ])
    } else {
        random_list(breadth, || generate_nested_dataset(size / breadth, depth - 1, breadth))
    }
}


fn generate_kv_dataset(size: usize, key_length: usize) -> SerializableData {
    random_list(size / 100, || random_kvpair(key_length, random_bigfloat))
}
