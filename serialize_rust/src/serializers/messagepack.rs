use crate::{data::SerializableData, serializer::Serializer};

pub struct MessagepackSerializer;

impl Serializer for MessagepackSerializer {
    fn serialize(data: &SerializableData) -> Result<Vec<u8>, String> {
        todo!()
    }
}