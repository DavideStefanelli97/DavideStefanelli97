// Extracts frames from the approved ASCII Magic preview without reimplementing its art.
const fs = require('fs');
const vm = require('vm');

const source = fs.readFileSync(process.argv[2], 'utf8');
const start = source.indexOf('<script>') + '<script>'.length;
const end = source.indexOf('const { meta, create } = Piece;', start);
if (start < '<script>'.length || end < 0) throw new Error('Preview script not found');
const code = source.slice(start, end) + '\n' +
  'globalThis.render = (() => { const draw = Piece.create(); return (t) => Glyphs.restyle(draw(t), Piece.meta.palette, {look:"dense"}); })();';
const context = {};
vm.runInNewContext(code, context, { filename: 'approved-preview.js' });
for (let i = 0; i < 190; i++) {
  const t = (5.5 + i / 20) % 9.5;
  process.stdout.write(JSON.stringify(context.render(t)) + '\n');
}
