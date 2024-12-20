use crate::{data::SerializableData, serializer::Serializer};

pub struct JSONSerializer;

impl Serializer for JSONSerializer {
    fn serialize(data: &SerializableData) -> Result<Vec<u8>, String> {
        serde_json::to_vec(&data).map_err(|err| err.to_string())
    }
    
    fn deserialize(data: &Vec<u8>) -> Result<SerializableData, String> {
        serde_json::from_slice(data).map_err(|err| err.to_string())
    }
}