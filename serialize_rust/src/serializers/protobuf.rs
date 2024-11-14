use crate::{data::SerializableData, serializer::Serializer};

pub struct ProtobufSerializer;

impl Serializer for ProtobufSerializer {
    fn serialize(data: &SerializableData) -> Result<String, String> {
        todo!()
    }
}