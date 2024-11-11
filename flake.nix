{
  description = "Python Packages Example";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/23.11";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem
      (system:
        let
          pkgs = import nixpkgs {
            inherit system;
          };

          python = pkgs.python3.override {
            self = python;
            packageOverrides = python-self: python-super: { };
          };

        in
        with pkgs;
        {
          devShells.default = mkShell {
            name = "Bot Flake";
            packages = [
              # Python packages:
              (python.withPackages (p: with p; [
                requests
                discordpy
              ]))
            ];

            shellHook = ''
            echo "Look at all these amazing Python packages!"
            '';
          };
        }
      );
}
