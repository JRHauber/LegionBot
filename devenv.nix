{ pkgs, inputs, ... }:
let
  pkgs-unstable = import inputs.nixpkgs-unstable { system = pkgs.stdenv.system; };

  matcha = pkgs.rustPlatform.buildRustPackage rec {
    pname = "matcha";
    version = "0.19.0";

    src = pkgs.fetchFromGitHub {
      owner = "michaeljones";
      repo = pname;
      rev = "137c325cf153fbbfb80768fd5a526f09fb2c35eb";
      hash = "sha256-Yz1eGbE97NsEA/mKlo1y19w8Dp0r+548XeSeCfFoRFQ=";
    };
    # cargoHash = lib.fakeHash;
    cargoHash = "sha256-7wFu0B39mIp54I0PA0F/IIdu7oF976cotsISnEU+oEc=";
  };
in
{
  env.PGHOST = "localhost";
  # env.PGPORT = "5432";
  env.PGUSER = "ben";
  env.PGDATABASE = "ben";
  env.PGPASSWORD = "";

  languages = {
    nix = {
      enable = true;
    };
    gleam = {
      enable = true;
      package = pkgs-unstable.gleam;
    };
  };

  packages = [
    pkgs-unstable.erlang_28
    pkgs-unstable.gleam
    pkgs-unstable.rebar3
    pkgs-unstable.elixir
    pkgs-unstable.glas
    pkgs-unstable.vscode-extensions.gleam.gleam
    matcha
  ];

  enterShell = ''
    echo "hello"
  '';

  services = {
    postgres = {
      enable = true;
      initialDatabases = [{ name = "centurion"; schema = ./init.sql;}];
      extensions = extensions: [];
      initialScript = "CREATE EXTENSION IF NOT EXISTS pgcrypto;";
      listen_addresses = "127.0.0.1";
    };
  };

  cachix.enable = false;
}
