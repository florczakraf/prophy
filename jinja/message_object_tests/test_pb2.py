# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: test.proto

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)




DESCRIPTOR = _descriptor.FileDescriptor(
  name='test.proto',
  package='',
  serialized_pb='\n\ntest.proto\"0\n\x07Message\x12\x13\n\x0bprotocol_id\x18\x01 \x02(\x05\x12\x10\n\x08msg_type\x18\x02 \x02(\x05')




_MESSAGE = _descriptor.Descriptor(
  name='Message',
  full_name='Message',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='protocol_id', full_name='Message.protocol_id', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='msg_type', full_name='Message.msg_type', index=1,
      number=2, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=14,
  serialized_end=62,
)

DESCRIPTOR.message_types_by_name['Message'] = _MESSAGE

class Message(_message.Message):
  __metaclass__ = _reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _MESSAGE

  # @@protoc_insertion_point(class_scope:Message)


# @@protoc_insertion_point(module_scope)