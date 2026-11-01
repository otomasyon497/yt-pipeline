import {H, W} from './geometry';

// Deterministic text widths (Inter, em units) so label placement is identical in every render tab.
const NARROW = new Set('ijl.,:;\'|!');
const SEMI = new Set('frtI1 ()-');
const WIDE = new Set('mwMW@');
export const textWidth = (text: string, size: number, spacing = 0, upper = false): number => {
	let em = 0;
	for (const ch of upper ? text.toUpperCase() : text) {
		if (NARROW.has(ch)) em += 0.28;
		else if (SEMI.has(ch)) em += 0.38;
		else if (WIDE.has(ch)) em += 0.86;
		else if (ch >= 'A' && ch <= 'Z') em += 0.68;
		else if (ch >= '0' && ch <= '9') em += 0.6;
		else em += 0.56;
	}
	return em * size + spacing * Math.max(0, text.length - 1);
};

export type LabelReq = {
	id: string;
	x: number; // anchor in screen px
	y: number;
	w: number; // text box
	h: number;
	r: number; // marker radius (0 = centred label, no marker)
	priority: number; // lower is placed first
};
export type Placement = {dx: number; dy: number; anchor: 'start' | 'middle' | 'end'; visible: boolean};

type Box = [number, number, number, number];
const overlaps = (a: Box, b: Box) => a[0] < b[2] && b[0] < a[2] && a[1] < b[3] && b[1] < a[3];

// Candidate offsets around a marker (text baseline at dy): right, left, above, below, then diagonals.
const candidates = (req: LabelReq): Placement[] => {
	if (req.r === 0) {
		return [
			{dx: 0, dy: req.h * 0.35, anchor: 'middle', visible: true},
			{dx: 0, dy: -req.h * 0.75, anchor: 'middle', visible: true},
			{dx: 0, dy: req.h * 1.35, anchor: 'middle', visible: true},
		];
	}
	const g = req.r + 10;
	const base = req.h * 0.35;
	return [
		{dx: g, dy: base, anchor: 'start', visible: true},
		{dx: -g, dy: base, anchor: 'end', visible: true},
		{dx: 0, dy: -g - req.h * 0.25, anchor: 'middle', visible: true},
		{dx: 0, dy: g + req.h * 0.8, anchor: 'middle', visible: true},
		{dx: g * 0.8, dy: -g * 0.6, anchor: 'start', visible: true},
		{dx: g * 0.8, dy: g + req.h * 0.5, anchor: 'start', visible: true},
		{dx: -g * 0.8, dy: -g * 0.6, anchor: 'end', visible: true},
		{dx: -g * 0.8, dy: g + req.h * 0.5, anchor: 'end', visible: true},
	];
};

const boxOf = (req: LabelReq, p: Placement): Box => {
	const x0 = p.anchor === 'start' ? req.x + p.dx : p.anchor === 'end' ? req.x + p.dx - req.w : req.x + p.dx - req.w / 2;
	const yb = req.y + p.dy; // baseline
	return [x0 - 6, yb - req.h * 0.9 - 4, x0 + req.w + 6, yb + req.h * 0.25 + 4];
};

// Greedy placement. `previous` keeps a label where it was if that spot is still free (no jumping).
export const placeLabels = (reqs: LabelReq[], safeBottom: number, previous: Map<string, Placement>): Map<string, Placement> => {
	const out = new Map<string, Placement>();
	const taken: Box[] = [];
	const bounds: Box = [24, 24, W - 24, H - safeBottom + 40];
	const inside = (b: Box) => b[0] >= bounds[0] && b[1] >= bounds[1] && b[2] <= bounds[2] && b[3] <= bounds[3];
	// Markers are obstacles for every label but their own.
	const markers = reqs.filter((r) => r.r > 0).map((r) => ({id: r.id, box: [r.x - r.r - 2, r.y - r.r - 2, r.x + r.r + 2, r.y + r.r + 2] as Box}));
	const free = (b: Box, id: string) => inside(b) && !taken.some((t) => overlaps(t, b)) && !markers.some((m) => m.id !== id && overlaps(m.box, b));
	for (const req of [...reqs].sort((a, b) => a.priority - b.priority)) {
		const prev = previous.get(req.id);
		const options = prev && prev.visible ? [prev, ...candidates(req)] : candidates(req);
		const hit = options.find((p) => free(boxOf(req, p), req.id));
		if (hit) {
			taken.push(boxOf(req, hit));
			out.set(req.id, {...hit, visible: true});
		} else {
			out.set(req.id, {...(prev ?? candidates(req)[0]), visible: false});
		}
	}
	return out;
};
