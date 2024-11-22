use crate::{data::SerializableData, serializer::Serializer};

pub struct JSONSerializer;

impl Serializer for JSONSerializer {
    fn serialize(data: &SerializableData) -> Result<String, String> {
        serde_json::to_string(&data).map_err(|err| err.to_string())
    }
}