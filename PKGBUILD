# Maintainer: fy59 / labfytools
# CONTRACT: coexistence avec swayfx ; ce paquet possède uniquement
# /usr/bin/swayfx-mosaic et n'annonce aucun remplacement de sway/swayfx.
pkgname=swayfx-mosaic
pkgver=0.6+mosaic.1
pkgrel=1
pkgdesc='SwayFX 0.6 with the native Mosaic / Spatial Canvas layout'
arch=('x86_64')
url='https://git.labfytools.com/fy59/swayfx-mosaic'
license=('MIT')
options=('!debug')
depends=('cairo' 'gdk-pixbuf2' 'libevdev' 'libinput' 'json-c'
         'systemd-libs' 'wayland' 'libxcb' 'libxkbcommon' 'pango' 'pcre2'
         'scenefx' 'ttf-font' 'wlroots0.20')
makedepends=('git' 'meson' 'ninja' 'pkgconf' 'python' 'wayland-protocols'
             'libdrm' 'pixman')
checkdepends=('kitty' 'grim')
_upstream_commit=fd71a6bdc061bd633b488ae7b83e8a6981d22f86
source=("swayfx::git+https://github.com/WillPower3309/swayfx.git#commit=${_upstream_commit}"
        "mosaic.patch::file://${startdir}/patches/0001-mosaic-layout-viewport.patch"
        "headless-ipc.py::file://${startdir}/tests/headless-ipc.py")
sha256sums=('SKIP'
            'a04cd06a6ef4fc58e3b40333a53226849e82d9a4757b9ccee58ad7b59a23ff4b'
            '0a16c887ca6a87f0392c2eef498b4fad78b9f32afaf7d2a6c0e5e0e37c3c1744')

prepare() {
    cd "$srcdir/swayfx"
    # No automatic forward port: an upstream commit change must be reviewed.
    [[ $(git rev-parse HEAD) == "$_upstream_commit" ]] || return 1
    git apply --check "$srcdir/mosaic.patch" || return 1
    git apply "$srcdir/mosaic.patch"
}

build() {
    meson setup "$srcdir/swayfx" "$srcdir/build-mosaic" \
        --prefix=/usr --bindir=bin \
        -Dwerror=false -Dsd-bus-provider=libsystemd \
        -Dmosaic-package=true -Dswaybar=false -Dswaynag=false \
        -Dman-pages=disabled -Ddefault-wallpaper=false
    meson compile -C "$srcdir/build-mosaic"
}

check() {
    meson test -C "$srcdir/build-mosaic" --print-errorlogs
    MOSAIC_BINARY="$srcdir/build-mosaic/sway/swayfx-mosaic" \
        python "$srcdir/headless-ipc.py"
}

package() {
    meson install -C "$srcdir/build-mosaic" --destdir "$pkgdir"
    [[ -x "$pkgdir/usr/bin/swayfx-mosaic" ]] || return 1
    [[ $(find "$pkgdir" -type f | wc -l) -eq 1 ]] || return 1
}
