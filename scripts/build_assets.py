"""Concatenate CSS/JS for fewer HTTP/1.1 round-trips on the VPS."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATIC = ROOT / 'static'

FONT_CSS = """
@font-face {
  font-family: 'Plus Jakarta Sans';
  font-style: normal;
  font-weight: 400;
  font-display: swap;
  src: url('../fonts/plus-jakarta-sans-latin.woff2') format('woff2');
  unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD;
}
@font-face {
  font-family: 'Plus Jakarta Sans';
  font-style: normal;
  font-weight: 600;
  font-display: swap;
  src: url('../fonts/plus-jakarta-sans-latin-600.woff2') format('woff2');
  unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD;
}
@font-face {
  font-family: 'Plus Jakarta Sans';
  font-style: normal;
  font-weight: 700;
  font-display: swap;
  src: url('../fonts/plus-jakarta-sans-latin-700.woff2') format('woff2');
  unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD;
}
@font-face {
  font-family: 'Plus Jakarta Sans';
  font-style: normal;
  font-weight: 800;
  font-display: swap;
  src: url('../fonts/plus-jakarta-sans-latin-800.woff2') format('woff2');
  unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD;
}
"""


def concat(paths, out, header=''):
    parts = [header.rstrip() + '\n\n'] if header else []
    for path in paths:
        parts.append(f'/* === {path.name} === */\n')
        parts.append(path.read_text(encoding='utf-8'))
        parts.append('\n')
    out.write_text(''.join(parts), encoding='utf-8')
    print(f'Wrote {out.relative_to(ROOT)} ({out.stat().st_size // 1024} KB)')


def main():
    concat(
        [
            STATIC / 'css' / 'main.css',
            STATIC / 'css' / 'pages.css',
            STATIC / 'css' / 'responsive.css',
        ],
        STATIC / 'css' / 'site.css',
        header=FONT_CSS,
    )
    concat(
        [
            STATIC / 'js' / 'theme.js',
            STATIC / 'js' / 'nav.js',
            STATIC / 'js' / 'hero-rotator.js',
        ],
        STATIC / 'js' / 'site.js',
    )


if __name__ == '__main__':
    main()
