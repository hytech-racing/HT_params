{pkgs, python311, protobuf, CASE_lib }:

pkgs.stdenv.mkDerivation rec {
  name = "ht_eth_protos";
  
  src = ./proto_gen;
  
  buildInputs = [ python311 protobuf ]; # Python as a build dependency
  
  # Define the build phase to execute the scripts
  buildPhase = ''
    # Run the Python script
    ${python311}/bin/python gen_proto.py ${CASE_lib}/CASEParameters.json
    protoc --include_imports --descriptor_set_out=ht_eth.bin ht_eth.proto
  '';

  # Specify the output of the build process
  # In this case, it will be the generated file
  installPhase = ''
    mkdir -p $out/proto
    mkdir -p $out/bin
    mkdir -p $out/include
    cp default_config.h $out/include
    cp ht_eth.proto $out/proto
    cp ht_eth.bin $out/bin
  '';
}