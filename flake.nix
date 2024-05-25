{
  description = "flake for generating ethernet proto msgs and nanopb lib from that proto";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-23.11";
    flake-utils.url = "github:numtide/flake-utils";
    nix-proto = { url = "github:notalltim/nix-proto"; };
  };

  outputs =
    { self
    , nixpkgs
    , flake-utils
    , nix-proto
    , ...
    }@inputs:
    flake-utils.lib.eachSystem [ "x86_64-linux" "aarch64-darwin" "x86_64-darwin" "aarch64-linux" ] (system:
    let
      params_interface_overlay = final: prev: {
        params_interface = final.callPackage ./default.nix { };
      };
      ht_eth_protos_overlay = final: prev: {
        # package that has the "final" hytech_eth.proto file
        ht_eth_protos_gen_pkg = final.callPackage ./generate_proto.nix { };
      };
      

      nix_protos_eth_overlays = nix-proto.generateOverlays' {
        hytech_eth_np = { ht_eth_protos_gen_pkg }:
          nix-proto.mkProtoDerivation {
            name = "hytech_eth_np";
            buildInputs = [ ht_eth_protos_gen_pkg ];
            src = ht_eth_protos_gen_pkg.out + "/proto";
            version = "1.0.0";
          };
      };
      my_overlays = [
        params_interface_overlay
        ht_eth_protos_overlay
      ] ++ nix-proto.lib.overlayToList nix_protos_eth_overlays;
      pkgs = import nixpkgs {
        overlays = my_overlays;
        inherit system;
      };
      nanopb_runner = pkgs.writeShellScriptBin "run-nanopb" ''
        #!${pkgs.stdenv.shell}
        export PATH="${pkgs.protobuf}/bin:$PATH"
        ${pkgs.nanopb}/bin/nanopb_generator.py -I=${pkgs.ht_eth_protos_gen_pkg}/proto ht_eth.proto
        cp ${pkgs.ht_eth_protos_gen_pkg}/proto/ht_eth.proto .
        cp ${pkgs.ht_eth_protos_gen_pkg}/include/* .
      '';

      shared_shell = pkgs.mkShell rec {
        name = "nix-devshell";
        packages = with pkgs; [
          params_interface
          ht_eth_protos_gen_pkg
        ];
      };
      
    in
    {
      overlays = my_overlays;
      devShells = {
        default = shared_shell;
      };

      packages = rec {
        default = pkgs.params_interface;
        hytech_eth_np_proto_py = pkgs.hytech_eth_np_proto_py;
        nanopbRunner = nanopb_runner;
      };

      apps = {
        nanopb-runner = flake-utils.lib.mkApp {
          drv = nanopb_runner;
        };
      };

    });
}