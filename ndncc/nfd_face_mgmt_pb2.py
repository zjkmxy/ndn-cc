# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: nfd-face-mgmt.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='nfd-face-mgmt.proto',
  package='ndn_message',
  syntax='proto2',
  serialized_options=None,
  serialized_pb=_b('\n\x13nfd-face-mgmt.proto\x12\x0bndn_message\"\x19\n\x04Name\x12\x11\n\tcomponent\x18\x08 \x03(\x0c\"\xba\x02\n\x1c\x46\x61\x63\x65\x45ventNotificationMessage\x12\x61\n\x17\x66\x61\x63\x65_event_notification\x18\xc0\x01 \x02(\x0b\x32?.ndn_message.FaceEventNotificationMessage.FaceEventNotification\x1a\xb6\x01\n\x15\x46\x61\x63\x65\x45ventNotification\x12\x18\n\x0f\x66\x61\x63\x65_event_kind\x18\xc1\x01 \x02(\r\x12\x0f\n\x07\x66\x61\x63\x65_id\x18i \x02(\x04\x12\x0b\n\x03uri\x18r \x02(\x0c\x12\x12\n\tlocal_uri\x18\x81\x01 \x02(\x0c\x12\x13\n\nface_scope\x18\x84\x01 \x02(\r\x12\x19\n\x10\x66\x61\x63\x65_persistency\x18\x85\x01 \x02(\r\x12\x12\n\tlink_type\x18\x86\x01 \x02(\r\x12\r\n\x05\x66lags\x18l \x02(\x04\"\xa9\x03\n\x15\x43ontrolCommandMessage\x12P\n\x12\x63ontrol_parameters\x18h \x02(\x0b\x32\x34.ndn_message.ControlCommandMessage.ControlParameters\x1a\xbd\x02\n\x11\x43ontrolParameters\x12\x1f\n\x04name\x18\x07 \x01(\x0b\x32\x11.ndn_message.Name\x12\x0f\n\x07\x66\x61\x63\x65_id\x18i \x01(\x04\x12\x0b\n\x03uri\x18r \x01(\x0c\x12\x12\n\tlocal_uri\x18\x81\x01 \x01(\x0c\x12\x0e\n\x06origin\x18o \x01(\x04\x12\x0c\n\x04\x63ost\x18j \x01(\x04\x12\x11\n\x08\x63\x61pacity\x18\x83\x01 \x01(\x04\x12\x0e\n\x05\x63ount\x18\x84\x01 \x01(\x04\x12\x17\n\x0e\x62\x61se_cong_mark\x18\x87\x01 \x01(\x04\x12\x17\n\x0e\x64\x65\x66_cong_thres\x18\x88\x01 \x01(\x04\x12\x0c\n\x03mtu\x18\x89\x01 \x01(\x04\x12\r\n\x05\x66lags\x18l \x01(\x04\x12\x0c\n\x04mask\x18p \x01(\x04\x12#\n\x08strategy\x18k \x01(\x0b\x32\x11.ndn_message.Name\x12\x12\n\nexp_period\x18m \x01(\x04\"\x9c\x01\n\x16\x43ontrolResponseMessage\x12M\n\x10\x63ontrol_response\x18\x65 \x02(\x0b\x32\x33.ndn_message.ControlResponseMessage.ControlResponse\x1a\x33\n\x0f\x43ontrolResponse\x12\x0f\n\x07st_code\x18\x66 \x01(\x04\x12\x0f\n\x07st_text\x18g \x01(\x0c\"\xa4\x05\n\rGeneralStatus\x12\x14\n\x0bnfd_version\x18\x80\x01 \x01(\x0c\x12\x18\n\x0fstart_timestamp\x18\x81\x01 \x01(\x04\x12\x1a\n\x11\x63urrent_timestamp\x18\x82\x01 \x01(\x04\x12\x1c\n\x13n_name_tree_entries\x18\x83\x01 \x01(\x04\x12\x16\n\rn_fib_entries\x18\x84\x01 \x01(\x04\x12\x16\n\rn_pit_entries\x18\x85\x01 \x01(\x04\x12\x1e\n\x15n_measurement_entries\x18\x86\x01 \x01(\x04\x12\x15\n\x0cn_cs_entries\x18\x87\x01 \x01(\x04\x12\x17\n\x0en_in_interests\x18\x90\x01 \x01(\x04\x12\x12\n\tn_in_data\x18\x91\x01 \x01(\x04\x12\x13\n\nn_in_nacks\x18\x97\x01 \x01(\x04\x12\x18\n\x0fn_out_interests\x18\x92\x01 \x01(\x04\x12\x13\n\nn_out_data\x18\x93\x01 \x01(\x04\x12\x14\n\x0bn_out_nacks\x18\x98\x01 \x01(\x04\x12\x1e\n\x15n_satisfied_interests\x18\x99\x01 \x01(\x04\x12 \n\x17n_unsatisfied_interests\x18\x9a\x01 \x01(\x04\x12\x1f\n\x16n_fragmentation_errors\x18\xc8\x01 \x01(\x04\x12\x17\n\x0en_out_over_mtu\x18\xc9\x01 \x01(\x04\x12\x18\n\x0fn_in_lp_invalid\x18\xca\x01 \x01(\x04\x12\x1e\n\x15n_reassembly_timeouts\x18\xcb\x01 \x01(\x04\x12\x19\n\x10n_in_net_invalid\x18\xcc\x01 \x01(\x04\x12\x17\n\x0en_acknowledged\x18\xcd\x01 \x01(\x04\x12\x18\n\x0fn_retransmitted\x18\xce\x01 \x01(\x04\x12\x19\n\x10n_retx_exhausted\x18\xcf\x01 \x01(\x04\x12\x1c\n\x13n_congestion_marked\x18\xd0\x01 \x01(\x04')
)




_NAME = _descriptor.Descriptor(
  name='Name',
  full_name='ndn_message.Name',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='component', full_name='ndn_message.Name.component', index=0,
      number=8, type=12, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=36,
  serialized_end=61,
)


_FACEEVENTNOTIFICATIONMESSAGE_FACEEVENTNOTIFICATION = _descriptor.Descriptor(
  name='FaceEventNotification',
  full_name='ndn_message.FaceEventNotificationMessage.FaceEventNotification',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='face_event_kind', full_name='ndn_message.FaceEventNotificationMessage.FaceEventNotification.face_event_kind', index=0,
      number=193, type=13, cpp_type=3, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='face_id', full_name='ndn_message.FaceEventNotificationMessage.FaceEventNotification.face_id', index=1,
      number=105, type=4, cpp_type=4, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='uri', full_name='ndn_message.FaceEventNotificationMessage.FaceEventNotification.uri', index=2,
      number=114, type=12, cpp_type=9, label=2,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='local_uri', full_name='ndn_message.FaceEventNotificationMessage.FaceEventNotification.local_uri', index=3,
      number=129, type=12, cpp_type=9, label=2,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='face_scope', full_name='ndn_message.FaceEventNotificationMessage.FaceEventNotification.face_scope', index=4,
      number=132, type=13, cpp_type=3, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='face_persistency', full_name='ndn_message.FaceEventNotificationMessage.FaceEventNotification.face_persistency', index=5,
      number=133, type=13, cpp_type=3, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='link_type', full_name='ndn_message.FaceEventNotificationMessage.FaceEventNotification.link_type', index=6,
      number=134, type=13, cpp_type=3, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='flags', full_name='ndn_message.FaceEventNotificationMessage.FaceEventNotification.flags', index=7,
      number=108, type=4, cpp_type=4, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=196,
  serialized_end=378,
)

_FACEEVENTNOTIFICATIONMESSAGE = _descriptor.Descriptor(
  name='FaceEventNotificationMessage',
  full_name='ndn_message.FaceEventNotificationMessage',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='face_event_notification', full_name='ndn_message.FaceEventNotificationMessage.face_event_notification', index=0,
      number=192, type=11, cpp_type=10, label=2,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[_FACEEVENTNOTIFICATIONMESSAGE_FACEEVENTNOTIFICATION, ],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=64,
  serialized_end=378,
)


_CONTROLCOMMANDMESSAGE_CONTROLPARAMETERS = _descriptor.Descriptor(
  name='ControlParameters',
  full_name='ndn_message.ControlCommandMessage.ControlParameters',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='name', full_name='ndn_message.ControlCommandMessage.ControlParameters.name', index=0,
      number=7, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='face_id', full_name='ndn_message.ControlCommandMessage.ControlParameters.face_id', index=1,
      number=105, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='uri', full_name='ndn_message.ControlCommandMessage.ControlParameters.uri', index=2,
      number=114, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='local_uri', full_name='ndn_message.ControlCommandMessage.ControlParameters.local_uri', index=3,
      number=129, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='origin', full_name='ndn_message.ControlCommandMessage.ControlParameters.origin', index=4,
      number=111, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='cost', full_name='ndn_message.ControlCommandMessage.ControlParameters.cost', index=5,
      number=106, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='capacity', full_name='ndn_message.ControlCommandMessage.ControlParameters.capacity', index=6,
      number=131, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='count', full_name='ndn_message.ControlCommandMessage.ControlParameters.count', index=7,
      number=132, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='base_cong_mark', full_name='ndn_message.ControlCommandMessage.ControlParameters.base_cong_mark', index=8,
      number=135, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='def_cong_thres', full_name='ndn_message.ControlCommandMessage.ControlParameters.def_cong_thres', index=9,
      number=136, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='mtu', full_name='ndn_message.ControlCommandMessage.ControlParameters.mtu', index=10,
      number=137, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='flags', full_name='ndn_message.ControlCommandMessage.ControlParameters.flags', index=11,
      number=108, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='mask', full_name='ndn_message.ControlCommandMessage.ControlParameters.mask', index=12,
      number=112, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='strategy', full_name='ndn_message.ControlCommandMessage.ControlParameters.strategy', index=13,
      number=107, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='exp_period', full_name='ndn_message.ControlCommandMessage.ControlParameters.exp_period', index=14,
      number=109, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=489,
  serialized_end=806,
)

_CONTROLCOMMANDMESSAGE = _descriptor.Descriptor(
  name='ControlCommandMessage',
  full_name='ndn_message.ControlCommandMessage',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='control_parameters', full_name='ndn_message.ControlCommandMessage.control_parameters', index=0,
      number=104, type=11, cpp_type=10, label=2,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[_CONTROLCOMMANDMESSAGE_CONTROLPARAMETERS, ],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=381,
  serialized_end=806,
)


_CONTROLRESPONSEMESSAGE_CONTROLRESPONSE = _descriptor.Descriptor(
  name='ControlResponse',
  full_name='ndn_message.ControlResponseMessage.ControlResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='st_code', full_name='ndn_message.ControlResponseMessage.ControlResponse.st_code', index=0,
      number=102, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='st_text', full_name='ndn_message.ControlResponseMessage.ControlResponse.st_text', index=1,
      number=103, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=914,
  serialized_end=965,
)

_CONTROLRESPONSEMESSAGE = _descriptor.Descriptor(
  name='ControlResponseMessage',
  full_name='ndn_message.ControlResponseMessage',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='control_response', full_name='ndn_message.ControlResponseMessage.control_response', index=0,
      number=101, type=11, cpp_type=10, label=2,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[_CONTROLRESPONSEMESSAGE_CONTROLRESPONSE, ],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=809,
  serialized_end=965,
)


_GENERALSTATUS = _descriptor.Descriptor(
  name='GeneralStatus',
  full_name='ndn_message.GeneralStatus',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='nfd_version', full_name='ndn_message.GeneralStatus.nfd_version', index=0,
      number=128, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='start_timestamp', full_name='ndn_message.GeneralStatus.start_timestamp', index=1,
      number=129, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='current_timestamp', full_name='ndn_message.GeneralStatus.current_timestamp', index=2,
      number=130, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='n_name_tree_entries', full_name='ndn_message.GeneralStatus.n_name_tree_entries', index=3,
      number=131, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='n_fib_entries', full_name='ndn_message.GeneralStatus.n_fib_entries', index=4,
      number=132, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='n_pit_entries', full_name='ndn_message.GeneralStatus.n_pit_entries', index=5,
      number=133, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='n_measurement_entries', full_name='ndn_message.GeneralStatus.n_measurement_entries', index=6,
      number=134, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='n_cs_entries', full_name='ndn_message.GeneralStatus.n_cs_entries', index=7,
      number=135, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='n_in_interests', full_name='ndn_message.GeneralStatus.n_in_interests', index=8,
      number=144, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='n_in_data', full_name='ndn_message.GeneralStatus.n_in_data', index=9,
      number=145, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='n_in_nacks', full_name='ndn_message.GeneralStatus.n_in_nacks', index=10,
      number=151, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='n_out_interests', full_name='ndn_message.GeneralStatus.n_out_interests', index=11,
      number=146, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='n_out_data', full_name='ndn_message.GeneralStatus.n_out_data', index=12,
      number=147, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='n_out_nacks', full_name='ndn_message.GeneralStatus.n_out_nacks', index=13,
      number=152, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='n_satisfied_interests', full_name='ndn_message.GeneralStatus.n_satisfied_interests', index=14,
      number=153, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='n_unsatisfied_interests', full_name='ndn_message.GeneralStatus.n_unsatisfied_interests', index=15,
      number=154, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='n_fragmentation_errors', full_name='ndn_message.GeneralStatus.n_fragmentation_errors', index=16,
      number=200, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='n_out_over_mtu', full_name='ndn_message.GeneralStatus.n_out_over_mtu', index=17,
      number=201, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='n_in_lp_invalid', full_name='ndn_message.GeneralStatus.n_in_lp_invalid', index=18,
      number=202, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='n_reassembly_timeouts', full_name='ndn_message.GeneralStatus.n_reassembly_timeouts', index=19,
      number=203, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='n_in_net_invalid', full_name='ndn_message.GeneralStatus.n_in_net_invalid', index=20,
      number=204, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='n_acknowledged', full_name='ndn_message.GeneralStatus.n_acknowledged', index=21,
      number=205, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='n_retransmitted', full_name='ndn_message.GeneralStatus.n_retransmitted', index=22,
      number=206, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='n_retx_exhausted', full_name='ndn_message.GeneralStatus.n_retx_exhausted', index=23,
      number=207, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='n_congestion_marked', full_name='ndn_message.GeneralStatus.n_congestion_marked', index=24,
      number=208, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=968,
  serialized_end=1644,
)

_FACEEVENTNOTIFICATIONMESSAGE_FACEEVENTNOTIFICATION.containing_type = _FACEEVENTNOTIFICATIONMESSAGE
_FACEEVENTNOTIFICATIONMESSAGE.fields_by_name['face_event_notification'].message_type = _FACEEVENTNOTIFICATIONMESSAGE_FACEEVENTNOTIFICATION
_CONTROLCOMMANDMESSAGE_CONTROLPARAMETERS.fields_by_name['name'].message_type = _NAME
_CONTROLCOMMANDMESSAGE_CONTROLPARAMETERS.fields_by_name['strategy'].message_type = _NAME
_CONTROLCOMMANDMESSAGE_CONTROLPARAMETERS.containing_type = _CONTROLCOMMANDMESSAGE
_CONTROLCOMMANDMESSAGE.fields_by_name['control_parameters'].message_type = _CONTROLCOMMANDMESSAGE_CONTROLPARAMETERS
_CONTROLRESPONSEMESSAGE_CONTROLRESPONSE.containing_type = _CONTROLRESPONSEMESSAGE
_CONTROLRESPONSEMESSAGE.fields_by_name['control_response'].message_type = _CONTROLRESPONSEMESSAGE_CONTROLRESPONSE
DESCRIPTOR.message_types_by_name['Name'] = _NAME
DESCRIPTOR.message_types_by_name['FaceEventNotificationMessage'] = _FACEEVENTNOTIFICATIONMESSAGE
DESCRIPTOR.message_types_by_name['ControlCommandMessage'] = _CONTROLCOMMANDMESSAGE
DESCRIPTOR.message_types_by_name['ControlResponseMessage'] = _CONTROLRESPONSEMESSAGE
DESCRIPTOR.message_types_by_name['GeneralStatus'] = _GENERALSTATUS
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

Name = _reflection.GeneratedProtocolMessageType('Name', (_message.Message,), dict(
  DESCRIPTOR = _NAME,
  __module__ = 'nfd_face_mgmt_pb2'
  # @@protoc_insertion_point(class_scope:ndn_message.Name)
  ))
_sym_db.RegisterMessage(Name)

FaceEventNotificationMessage = _reflection.GeneratedProtocolMessageType('FaceEventNotificationMessage', (_message.Message,), dict(

  FaceEventNotification = _reflection.GeneratedProtocolMessageType('FaceEventNotification', (_message.Message,), dict(
    DESCRIPTOR = _FACEEVENTNOTIFICATIONMESSAGE_FACEEVENTNOTIFICATION,
    __module__ = 'nfd_face_mgmt_pb2'
    # @@protoc_insertion_point(class_scope:ndn_message.FaceEventNotificationMessage.FaceEventNotification)
    ))
  ,
  DESCRIPTOR = _FACEEVENTNOTIFICATIONMESSAGE,
  __module__ = 'nfd_face_mgmt_pb2'
  # @@protoc_insertion_point(class_scope:ndn_message.FaceEventNotificationMessage)
  ))
_sym_db.RegisterMessage(FaceEventNotificationMessage)
_sym_db.RegisterMessage(FaceEventNotificationMessage.FaceEventNotification)

ControlCommandMessage = _reflection.GeneratedProtocolMessageType('ControlCommandMessage', (_message.Message,), dict(

  ControlParameters = _reflection.GeneratedProtocolMessageType('ControlParameters', (_message.Message,), dict(
    DESCRIPTOR = _CONTROLCOMMANDMESSAGE_CONTROLPARAMETERS,
    __module__ = 'nfd_face_mgmt_pb2'
    # @@protoc_insertion_point(class_scope:ndn_message.ControlCommandMessage.ControlParameters)
    ))
  ,
  DESCRIPTOR = _CONTROLCOMMANDMESSAGE,
  __module__ = 'nfd_face_mgmt_pb2'
  # @@protoc_insertion_point(class_scope:ndn_message.ControlCommandMessage)
  ))
_sym_db.RegisterMessage(ControlCommandMessage)
_sym_db.RegisterMessage(ControlCommandMessage.ControlParameters)

ControlResponseMessage = _reflection.GeneratedProtocolMessageType('ControlResponseMessage', (_message.Message,), dict(

  ControlResponse = _reflection.GeneratedProtocolMessageType('ControlResponse', (_message.Message,), dict(
    DESCRIPTOR = _CONTROLRESPONSEMESSAGE_CONTROLRESPONSE,
    __module__ = 'nfd_face_mgmt_pb2'
    # @@protoc_insertion_point(class_scope:ndn_message.ControlResponseMessage.ControlResponse)
    ))
  ,
  DESCRIPTOR = _CONTROLRESPONSEMESSAGE,
  __module__ = 'nfd_face_mgmt_pb2'
  # @@protoc_insertion_point(class_scope:ndn_message.ControlResponseMessage)
  ))
_sym_db.RegisterMessage(ControlResponseMessage)
_sym_db.RegisterMessage(ControlResponseMessage.ControlResponse)

GeneralStatus = _reflection.GeneratedProtocolMessageType('GeneralStatus', (_message.Message,), dict(
  DESCRIPTOR = _GENERALSTATUS,
  __module__ = 'nfd_face_mgmt_pb2'
  # @@protoc_insertion_point(class_scope:ndn_message.GeneralStatus)
  ))
_sym_db.RegisterMessage(GeneralStatus)


# @@protoc_insertion_point(module_scope)
