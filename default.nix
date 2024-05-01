{ lib
, python311Packages
, hytech_eth_np_proto_py
}:

python311Packages.buildPythonApplication {
  pname = "params_interface";
  version = "1.0.0";

  propagatedBuildInputs = [
    
    python311Packages.protobuf
    hytech_eth_np_proto_py
  ];

  src = ./params_interface;
}