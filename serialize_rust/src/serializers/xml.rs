use crate::{data::SerializableData, serializer::Serializer};

pub struct XMLSerializer;

impl Serializer for XMLSerializer {
    fn serialize(data: &SerializableData) -> Result<Vec<u8>, String> {
        serde_xml_rs::to_string(&data).map_err(|err| err.to_string()).map(|string| string.into_bytes())
    }

    fn deserialize(data: &[u8]) -> Result<SerializableData, String> {
        let string = String::from_utf8(data.to_vec()).map_err(|err| err.to_string())?;
        serde_xml_rs::from_str(&string).map_err(|err| err.to_string())
    }
}