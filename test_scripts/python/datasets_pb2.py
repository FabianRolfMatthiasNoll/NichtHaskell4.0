# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: datasets.proto
# Protobuf Python Version: 5.28.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    28,
    1,
    '',
    'datasets.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0e\x64\x61tasets.proto\"f\n\x08KeyValue\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\x14\n\nbool_value\x18\x02 \x01(\x08H\x00\x12\x16\n\x0c\x64ouble_value\x18\x03 \x01(\x01H\x00\x12\x16\n\x0cstring_value\x18\x04 \x01(\tH\x00\x42\x07\n\x05value\"(\n\nNestedData\x12\x1a\n\x05items\x18\x01 \x03(\x0b\x32\x0b.NestedData\"\xa0\x01\n\tMixedData\x12\x13\n\tint_value\x18\x01 \x01(\x05H\x00\x12\x15\n\x0b\x66loat_value\x18\x02 \x01(\x02H\x00\x12\x16\n\x0cstring_value\x18\x03 \x01(\tH\x00\x12!\n\x0ckvpair_value\x18\x04 \x01(\x0b\x32\t.KeyValueH\x00\x12#\n\x0cnested_value\x18\x05 \x01(\x0b\x32\x0b.NestedDataH\x00\x42\x07\n\x05value\"&\n\tMixedList\x12\x19\n\x05items\x18\x01 \x03(\x0b\x32\n.MixedDatab\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'datasets_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_KEYVALUE']._serialized_start=18
  _globals['_KEYVALUE']._serialized_end=120
  _globals['_NESTEDDATA']._serialized_start=122
  _globals['_NESTEDDATA']._serialized_end=162
  _globals['_MIXEDDATA']._serialized_start=165
  _globals['_MIXEDDATA']._serialized_end=325
  _globals['_MIXEDLIST']._serialized_start=327
  _globals['_MIXEDLIST']._serialized_end=365
# @@protoc_insertion_point(module_scope)
