// Bake the SVG icon sources into the PNGs the add-on draws.
//
// Blender cannot rasterize SVG at draw time, so each icon in svg/ is
// rendered once per pixel size into png/<name>_<size>.png: white ink on
// transparent, tinted by the HUD when drawn. Every size is rendered from
// the vector, never scaled from another bitmap, so each one is as sharp
// as that size allows.
//
//   cd icons
//   npm install
//   node bake_icons.mjs
//
// Neither this script nor svg/ ships in the extension -- only png/.
//
// Another add-on that draws through hb_icons bakes its own icons with this
// same script, so they come out alike: pass its folder, which holds svg/
// and receives png/.
//
//   node bake_icons.mjs path/to/other_addon/icons

import { readFileSync, readdirSync, writeFileSync, mkdirSync } from 'node:fs';
import { dirname, join, basename, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { Resvg } from '@resvg/resvg-js';

// Icon heights in pixels. Sources are drawn on a 16-unit grid with 1px
// strokes on half-pixel lines, so 16 (100% UI scale) and its multiples are
// pixel-exact; 12 and 14 serve small chips, the rest are where the
// common resolution scales land. hb_icons.py picks the nearest one.
const SIZES = [12, 14, 16, 20, 24, 28, 32, 40, 48, 64];

const here = dirname(fileURLToPath(import.meta.url));
const root = process.argv[2] ? resolve(process.argv[2]) : here;
const srcDir = join(root, 'svg');
const outDir = join(root, 'png');
mkdirSync(outDir, { recursive: true });

let count = 0;
for (const file of readdirSync(srcDir).filter(f => f.endsWith('.svg'))) {
  const svg = readFileSync(join(srcDir, file));
  const name = basename(file, '.svg');
  for (const size of SIZES) {
    const png = new Resvg(svg, {
      fitTo: { mode: 'width', value: size },
      shapeRendering: 2,   // geometricPrecision: full antialiasing
    }).render().asPng();
    writeFileSync(join(outDir, `${name}_${size}.png`), png);
    count++;
  }
}
console.log(`Baked ${count} PNGs into ${outDir}`);
