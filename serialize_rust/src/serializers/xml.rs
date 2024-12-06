use std::io::Cursor;

use quick_xml::Writer;

use crate::{data::SerializableData, serializer::Serializer};

pub struct XMLSerializer;

impl Serializer for XMLSerializer {
    fn serialize(data: &SerializableData) -> Result<Vec<u8>, String> {
        serde_xml_rs::to_string(&data).map_err(|err| err.to_string()).map(|string| string.into_bytes())
    }
    
    fn deserialize(data: &Vec<u8>) -> Result<SerializableData, String> {
        serde_xml_rs::from_reader(data.as_slice()).map_err(|err| err.to_string())
    }
}