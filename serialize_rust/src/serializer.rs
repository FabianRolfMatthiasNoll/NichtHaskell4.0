use crate::data::SerializableData;

pub trait Serializer {
    fn serialize(data: &SerializableData) -> Result<Vec<u8>, String>;
    fn deserialize(data: &[u8]) -> Result<SerializableData, String>;
}