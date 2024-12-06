use core::fmt;

use serde::{de::{self, MapAccess, SeqAccess, Visitor}, ser::{SerializeMap, SerializeSeq}, Deserialize, Deserializer, Serialize, Serializer};

// arbitrary data
#[derive(Debug, Clone)]
pub enum SerializableData {
    Boolean(bool),
    Integer(i32),
    BigInteger(i64),
    Float(f32),
    BigFloat(f64),
    StringLiteral(String),
    KeyValuePair(String, Box<SerializableData>),
    List(Vec<SerializableData>),
}

impl SerializableData {
    // theoretical size of the actual payload data, without metadata
    // required to keep track of things such as string length, vector length
    // references or pointers.
    pub fn payload_size(&self) -> usize {
        match self {
            SerializableData::Boolean(_)                => 1,
            SerializableData::Integer(_)                => 4,
            SerializableData::BigInteger(_)             => 8,
            SerializableData::Float(_)                  => 4,
            SerializableData::BigFloat(_)               => 8,
            SerializableData::StringLiteral(literal)    => literal.len(),
            SerializableData::KeyValuePair(key, value)  => key.len() + value.payload_size(),
            SerializableData::List(vec)                 => vec.iter().map(|child| child.payload_size()).sum(),
        }
    }

    // actual size, in memory, of the given data. Contains "extra" stuff such as management
    // data for strings, vectors, etc.
    pub fn memory_size(&self) -> usize {
        match self {
            SerializableData::Integer(_)    |
            SerializableData::BigInteger(_) |
            SerializableData::Float(_)      |
            SerializableData::BigFloat(_)   |
            SerializableData::Boolean(_)                => std::mem::size_of::<SerializableData>(),
            SerializableData::StringLiteral(literal)    => std::mem::size_of::<SerializableData>() + literal.len(),
            SerializableData::KeyValuePair(key, value)  => std::mem::size_of::<SerializableData>() + key.len() + value.memory_size(),
            SerializableData::List(vec)                 => std::mem::size_of::<SerializableData>() + vec.iter().map(|child| child.memory_size()).sum::<usize>(),
        }
    }

    pub fn depth(&self) -> usize {
        match self {
            SerializableData::Boolean(_)                => 0,
            SerializableData::Integer(_)                => 0,
            SerializableData::BigInteger(_)             => 0,
            SerializableData::Float(_)                  => 0,
            SerializableData::BigFloat(_)               => 0,
            SerializableData::StringLiteral(_)          => 0,
            SerializableData::KeyValuePair(_, value)    => value.depth() + 1,
            SerializableData::List(vec)                 => vec.iter().map(|child| child.depth()).max().unwrap_or(0) + 1,
        }
    }
}

impl Serialize for SerializableData {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: Serializer,
    {
        match self {
            SerializableData::Boolean(value) => serializer.serialize_bool(*value),
            SerializableData::Integer(value) => serializer.serialize_i32(*value),
            SerializableData::BigInteger(value) => serializer.serialize_i64(*value),
            SerializableData::Float(value) => serializer.serialize_f32(*value),
            SerializableData::BigFloat(value) => serializer.serialize_f64(*value),
            SerializableData::StringLiteral(value) => serializer.serialize_str(value),
            SerializableData::KeyValuePair(key, value) => {
                let mut map = serializer.serialize_map(Some(1))?;
                map.serialize_entry(key, value)?;
                map.end()
            }
            SerializableData::List(values) => {
                let mut seq = serializer.serialize_seq(Some(values.len()))?;
                for value in values {
                    seq.serialize_element(value)?;
                }
                seq.end()
            }
        }
    }
}

impl<'de> Deserialize<'de> for SerializableData {
    fn deserialize<D>(deserializer: D) -> Result<Self, D::Error>
    where
        D: Deserializer<'de>,
    {
        struct SerializableDataVisitor;

        impl<'de> Visitor<'de> for SerializableDataVisitor {
            type Value = SerializableData;

            fn expecting(&self, formatter: &mut fmt::Formatter) -> fmt::Result {
                formatter.write_str("a SerializableData variant")
            }

            fn visit_bool<E>(self, value: bool) -> Result<Self::Value, E>
            where
                E: de::Error,
            {
                Ok(SerializableData::Boolean(value))
            }

            fn visit_i32<E>(self, value: i32) -> Result<Self::Value, E>
            where
                E: de::Error,
            {
                Ok(SerializableData::Integer(value))
            }

            fn visit_i64<E>(self, value: i64) -> Result<Self::Value, E>
            where
                E: de::Error,
            {
                Ok(SerializableData::BigInteger(value))
            }

            fn visit_u32<E>(self, value: u32) -> Result<Self::Value, E>
            where
                E: de::Error,
            {
                Ok(SerializableData::Integer(value as i32))
            }

            fn visit_u64<E>(self, value: u64) -> Result<Self::Value, E>
            where
                E: de::Error,
            {
                Ok(SerializableData::BigInteger(value as i64))
            }

            fn visit_f32<E>(self, value: f32) -> Result<Self::Value, E>
            where
                E: de::Error,
            {
                Ok(SerializableData::Float(value))
            }

            fn visit_f64<E>(self, value: f64) -> Result<Self::Value, E>
            where
                E: de::Error,
            {
                Ok(SerializableData::BigFloat(value))
            }

            fn visit_str<E>(self, value: &str) -> Result<Self::Value, E>
            where
                E: de::Error,
            {
                Ok(SerializableData::StringLiteral(value.to_string()))
            }

            fn visit_string<E>(self, value: String) -> Result<Self::Value, E>
            where
                E: de::Error,
            {
                Ok(SerializableData::StringLiteral(value))
            }

            fn visit_map<M>(self, mut access: M) -> Result<Self::Value, M::Error>
            where
                M: MapAccess<'de>,
            {
                if let Some((key, value)) = access.next_entry::<String, SerializableData>()? {
                    Ok(SerializableData::KeyValuePair(key, Box::new(value)))
                } else {
                    Err(de::Error::custom("Expected a key-value pair"))
                }
            }

            fn visit_seq<A>(self, mut access: A) -> Result<Self::Value, A::Error>
            where
                A: SeqAccess<'de>,
            {
                let mut elements = Vec::new();
                while let Some(element) = access.next_element::<SerializableData>()? {
                    elements.push(element);
                }
                Ok(SerializableData::List(elements))
            }
        }

        deserializer.deserialize_any(SerializableDataVisitor)
    }
}