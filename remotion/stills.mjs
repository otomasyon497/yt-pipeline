// Render selected frames of the Episode as JPEG stills (fast visual checks without a full render).
//   node stills.mjs <timeline.json> <out dir> <frame,frame,...>
import fs from 'node:fs';
import path from 'node:path';
import {bundle} from '@remotion/bundler';
import {renderStill, selectComposition} from '@remotion/renderer';

const [propsPath, outDir, frameList] = process.argv.slice(2);
const inputProps = JSON.parse(fs.readFileSync(propsPath, 'utf8'));
const frames = frameList
	.split(',')
	.map((s) => s.trim())
	.filter(Boolean)
	.map((s) => (s.endsWith('s') ? Math.round(parseFloat(s) * inputProps.fps) : parseInt(s, 10)))
	.filter((f) => f >= 0 && f < inputProps.totalFrames);
fs.mkdirSync(outDir, {recursive: true});
const serveUrl = await bundle({entryPoint: path.resolve('src/index.ts'), publicDir: path.resolve('public')});
const composition = await selectComposition({serveUrl, id: 'Episode', inputProps});
for (const frame of frames) {
	const t0 = Date.now();
	const output = path.join(outDir, `frame_${String(frame).padStart(5, '0')}.jpg`);
	await renderStill({composition, serveUrl, output, frame, inputProps, imageFormat: 'jpeg', jpegQuality: 88});
	console.log(`still ${frame} (${(frame / inputProps.fps).toFixed(1)}s) ${Date.now() - t0} ms`);
}
