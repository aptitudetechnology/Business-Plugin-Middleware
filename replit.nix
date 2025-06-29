{ pkgs }: {
  deps = [
    pkgs.python3
    pkgs.python3Packages.pip
    pkgs.python3Packages.flask
    pkgs.python3Packages.requests
    pkgs.python3Packages.python-dotenv
    pkgs.python3Packages.werkzeug
    pkgs.python3Packages.jinja2
    pkgs.tesseract
    pkgs.imagemagick
  ];
  
  env = {
    PYTHON_LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
      pkgs.stdenv.cc.cc.lib
      pkgs.zlib
      pkgs.glib
      pkgs.xorg.libX11
    ];
    PYTHONPATH = ".";
    FLASK_ENV = "development";
    FLASK_DEBUG = "1";
  };
}
