#!/usr/bin/env bash
# Installs the design/slicing toolchain this project uses, without root:
#   - OpenSCAD 2021.01 (parametric CAD; the mount designs in hardware/ are .scad)
#   - OrcaSlicer 2.4.2   (slicer with built-in Artillery Sidewinder X4 Plus profiles)
# Both are official AppImages, extracted with --appimage-extract so they run
# on hosts without FUSE, and exposed as wrapper scripts in ~/.local/bin.
# Re-running is safe: downloads and extractions are skipped if already present.
set -euo pipefail

# System prerequisites (the one part that needs root). OrcaSlicer's AppImage
# links against GTK3/WebKitGTK/GStreamer on the host, and xvfb lets it slice
# headless on a machine with no display. Ubuntu/Debian:
#   sudo apt-get install -y libwebkit2gtk-4.1-0 libgtk-3-0 libopengl0 \
#        libglu1-mesa libegl1 libgstreamer-plugins-base1.0-0 libsecret-1-0 xvfb
if ! ldconfig -p | grep -q libwebkit2gtk-4.1.so.0; then
  echo "WARNING: libwebkit2gtk-4.1 not found - OrcaSlicer will not start until the" >&2
  echo "         apt-get line at the top of this script has been run with sudo." >&2
fi

OPT="$HOME/.local/opt"
BIN="$HOME/.local/bin"
mkdir -p "$OPT" "$BIN"

OPENSCAD_URL="https://files.openscad.org/OpenSCAD-2021.01-x86_64.AppImage"
ORCA_URL="https://github.com/OrcaSlicer/OrcaSlicer/releases/download/v2.4.2/OrcaSlicer_Linux_AppImage_Ubuntu2404_V2.4.2.AppImage"

install_appimage() {
  local name="$1" url="$2" wrapper="$3"
  local dir="$OPT/$name"
  mkdir -p "$dir"
  if [ ! -f "$dir/$name.AppImage" ]; then
    echo "Downloading $name..."
    curl -L --fail --max-time 900 -o "$dir/$name.AppImage" "$url"
  fi
  chmod +x "$dir/$name.AppImage"
  if [ ! -d "$dir/squashfs-root" ]; then
    echo "Extracting $name..."
    (cd "$dir" && ./"$name.AppImage" --appimage-extract >/dev/null)
  fi
  # A wrapper, not a symlink: AppRun resolves its hook scripts relative to
  # its own location, so a symlink in ~/.local/bin breaks it.
  printf '#!/bin/sh\nexec "%s/squashfs-root/AppRun" "$@"\n' "$dir" > "$BIN/$wrapper"
  chmod +x "$BIN/$wrapper"
  echo "$wrapper -> $dir/squashfs-root/AppRun"
}

install_appimage openscad  "$OPENSCAD_URL" openscad
install_appimage orcaslicer "$ORCA_URL"    orca-slicer

# Headless slicing wrapper: runs Orca's CLI under a virtual X display.
cat > "$BIN/orca-slice-headless" <<'EOF'
#!/bin/sh
# usage: orca-slice-headless <orca-slicer CLI args...>
exec xvfb-run -a "$HOME/.local/bin/orca-slicer" "$@"
EOF
chmod +x "$BIN/orca-slice-headless"

echo
echo "Make sure $BIN is on your PATH, then:"
"$BIN/openscad" --version 2>&1 | head -1
echo "orca-slicer installed (headless use: orca-slicer --help)"
