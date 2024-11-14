use crate::{data::SerializableData, serializer::Serializer};

pub struct XMLSerializer;

impl Serializer for XMLSerializer {
    fn serialize(data: &SerializableData) -> Result<String, String> {
        serde_xml_rs::to_string(&data).map_err(|err| err.to_string())
    }
}