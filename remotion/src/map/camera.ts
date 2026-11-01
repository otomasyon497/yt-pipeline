import type {CamKey} from './types';

export type View = {x: number; y: number; w: number}; // centre and visible width, unit Mercator

export const easeInOut = (t: number) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);

// Smooth zoom-and-pan path (van Wijk & Nuij 2003, as in d3-interpolate's interpolateZoom).
// The same formula sizes the move durations in pipeline/maps.py (flight_length).
export const flight = (a: View, b: View, rho: number) => {
	const dx = b.x - a.x;
	const dy = b.y - a.y;
	const d2 = dx * dx + dy * dy;
	const rho2 = rho * rho;
	if (d2 < 1e-18) {
		const S = Math.log(b.w / a.w) / rho;
		return (t: number): View => ({x: a.x + t * dx, y: a.y + t * dy, w: a.w * Math.exp(rho * t * S)});
	}
	const d1 = Math.sqrt(d2);
	const b0 = (b.w * b.w - a.w * a.w + rho2 * rho2 * d2) / (2 * a.w * rho2 * d1);
	const b1 = (b.w * b.w - a.w * a.w - rho2 * rho2 * d2) / (2 * b.w * rho2 * d1);
	const r0 = Math.log(Math.sqrt(b0 * b0 + 1) - b0);
	const r1 = Math.log(Math.sqrt(b1 * b1 + 1) - b1);
	const S = (r1 - r0) / rho;
	const coshr0 = Math.cosh(r0);
	return (t: number): View => {
		const s = t * S;
		const u = (a.w / (rho2 * d1)) * (coshr0 * Math.tanh(rho * s + r0) - Math.sinh(r0));
		return {x: a.x + u * dx, y: a.y + u * dy, w: (a.w * coshr0) / Math.cosh(rho * s + r0)};
	};
};

// Camera over the whole block: eased flights between keyframes, then a slow push-in while holding.
export const makeCamera = (keys: CamKey[], rho: number, drift: number, fps: number) => {
	const sorted = [...keys].sort((p, q) => p.start - q.start);
	const flights: ((t: number) => View)[] = [];
	const segment = (k: number, f: number): View => {
		const key = sorted[k];
		const t = key.frames > 0 ? Math.min(1, Math.max(0, (f - key.start) / key.frames)) : 1;
		const v = t < 1 ? flights[k](easeInOut(t)) : {x: key.x, y: key.y, w: key.w};
		const held = Math.max(0, f - key.start - key.frames) / fps;
		return {x: v.x, y: v.y, w: v.w * Math.exp(-drift * Math.min(held, 9))};
	};
	sorted.forEach((key, k) => {
		const from = k === 0 ? {x: key.x, y: key.y, w: key.w} : segment(k - 1, key.start);
		flights.push(flight(from, key, rho));
	});
	const at = (f: number): View => {
		if (!sorted.length) return {x: 0.5, y: 0.45, w: 1};
		let k = -1;
		for (let i = 0; i < sorted.length; i++) if (sorted[i].start <= f) k = i;
		if (k < 0) return {x: sorted[0].x, y: sorted[0].y, w: sorted[0].w};
		return segment(k, f);
	};
	const arrivals = sorted.map((k) => k.start + k.frames);
	return {at, arrivals};
};
