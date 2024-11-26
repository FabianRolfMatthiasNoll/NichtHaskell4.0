use rand::{distributions::Alphanumeric, thread_rng, Rng};
use crate::data::SerializableData;

pub fn random_boolean() -> SerializableData {
    SerializableData::Boolean(rand::random())
}

pub fn random_int() -> SerializableData {
    SerializableData::Integer(rand::random())
}

pub fn random_bigint() -> SerializableData {
    SerializableData::BigInteger(rand::random())
}

pub fn random_float() -> SerializableData {
    SerializableData::Float(rand::random())
}

pub fn random_bigfloat() -> SerializableData {
    SerializableData::BigFloat(rand::random())
}

pub fn random_string(length: usize) -> SerializableData {
    SerializableData::StringLiteral(thread_rng().sample_iter(&Alphanumeric).take(length).map(char::from).collect())
}

pub fn random_list(length: usize, contents: impl Fn() -> SerializableData) -> SerializableData {
    SerializableData::List((0..length).map(|_| contents()).collect())
}

pub fn list(contents: Vec<impl Fn() -> SerializableData>) -> SerializableData {
    SerializableData::List(contents.iter().map(|generator| generator()).collect())
}

pub fn random_kvpair(keylength: usize, contents: impl Fn() -> SerializableData) -> SerializableData {
    let key = thread_rng().sample_iter(&Alphanumeric).take(keylength).map(char::from).collect();
    let value = Box::new(contents());
    SerializableData::KeyValuePair(key, value)
}

pub fn random_choice(choices: Vec<impl Fn() -> SerializableData>) -> SerializableData {
    choices[thread_rng().gen_range(0..choices.len())]()
}