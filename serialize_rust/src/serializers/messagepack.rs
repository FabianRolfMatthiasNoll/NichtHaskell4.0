use serde::Serialize;

use crate::{data::SerializableData, serializer::Serializer};

pub struct MessagepackSerializer;

impl Serializer for MessagepackSerializer {
    fn serialize(data: &SerializableData) -> Result<Vec<u8>, String> {
        let mut buf = Vec::new();
        match data.serialize(&mut rmp_serde::Serializer::new(&mut buf)) {
            Ok(_) => Ok(buf),
            Err(error) => Err(error.to_string()),
        }
    }
}