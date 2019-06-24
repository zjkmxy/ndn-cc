all: nfd_face_mgmt_pb2.py

nfd_face_mgmt_pb2.py: nfd-face-mgmt.proto
	/usr/local/bin/protoc --python_out=. nfd-face-mgmt.proto

