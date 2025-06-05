{
  pkgs ? import <nixpkgs> { },
}:

pkgs.mkShell {
  shellHook = ''
    exec zsh
  '';
  buildInputs = [
    pkgs.python3
    pkgs.python3Packages.tkinter
  ];
}
