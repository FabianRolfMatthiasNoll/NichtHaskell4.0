use crate::data::SerializableData;

pub trait Serializer {
    fn serialize(data: &SerializableData) -> Result<Vec<u8>, String>;
}