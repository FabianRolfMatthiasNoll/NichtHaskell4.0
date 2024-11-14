use crate::data::SerializableData;

pub trait Serializer {
    fn serialize(data: &SerializableData) -> Result<String, String>;
}