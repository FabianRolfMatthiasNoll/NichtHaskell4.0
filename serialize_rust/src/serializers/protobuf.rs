use crate::{data::SerializableData, data_protobuf::Data, serializer::Serializer};
use prost::Message;
pub struct ProtobufSerializer;

impl Serializer for ProtobufSerializer {
    fn serialize(data: &SerializableData) -> Result<Vec<u8>, String> {
        let protobuf_data: Data = Data::from(data.clone());
        Ok(protobuf_data.encode_to_vec())
    }
    
    fn deserialize(data: &[u8]) -> Result<SerializableData, String> {
        SerializableData::try_from(Data::decode(data).map_err(|err| err.to_string())?)
    }
}
