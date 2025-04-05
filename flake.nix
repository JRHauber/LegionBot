{
  description = "Development environment Gleam";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs,  ...}:
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.${system};

      matcha = pkgs.rustPlatform.buildRustPackage rec {
        pname = "matcha";
        version = "0.19.0";

        src = pkgs.fetchFromGitHub {
          owner = "michaeljones";
          repo = pname;
          rev = "137c325cf153fbbfb80768fd5a526f09fb2c35eb";
          hash = "sha256-Yz1eGbE97NsEA/mKlo1y19w8Dp0r+548XeSeCfFoRFQ=";
        };

        useFetchCargoVendor = true;
        # cargoHash = lib.fakeHash;
        cargoHash = "sha256-b+2pqRKCwjQhXoKC6tlJnNzysTQVSXtU/v0ry9aMNpM=";
      };

    in {
      devShells.${system}.default =
        pkgs.mkShell {

          buildInputs = [
            pkgs.erlang_28
            pkgs.gleam
            pkgs.rebar3
            pkgs.elixir
            pkgs.glas
            pkgs.vscode-extensions.gleam.gleam
            pkgs.gnumake42
            matcha
          ];
          # packages = [];
          shellHook = ''
            echo "shell ready"
            gleam --version
            matcha --version
          '';
        };
    };
}
