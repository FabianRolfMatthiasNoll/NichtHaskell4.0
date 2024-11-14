use std::collections::HashMap;
use serde::Serialize;

// arbitrary data
#[derive(Debug, Serialize)]
#[serde(untagged)]
pub enum SerializableData {
    Integer(i32),
    BigInteger(i64),
    Float(f32),
    BigFloat(f64),
    List(Vec<SerializableData>),
    Dict(HashMap<String, SerializableData>)
}

impl SerializableData {
    pub fn payload_size(&self) -> usize {
        match self {
            SerializableData::Integer(_)    => 4,
            SerializableData::BigInteger(_) => 8,
            SerializableData::Float(_)      => 4,
            SerializableData::BigFloat(_)   => 8,
            SerializableData::List(vec)     => vec.iter().map(|child| child.payload_size()).sum(),
            SerializableData::Dict(map)     => map.iter().map(|(key, val)| key.len() + val.payload_size()).sum(),
        }
    }

    pub fn depth(&self) -> usize {
        match self {
            SerializableData::Integer(_)    => 0,
            SerializableData::BigInteger(_) => 0,
            SerializableData::Float(_)      => 0,
            SerializableData::BigFloat(_)   => 0,
            SerializableData::List(vec)     => vec.iter().map(|child| child.depth()).max().unwrap_or(0) + 1,
            SerializableData::Dict(map)     => map.iter().map(|(_, val)| val.depth()).max().unwrap_or(0) + 1,
        }
    }
}
