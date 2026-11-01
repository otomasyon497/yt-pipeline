import type {View} from './camera';

export const W = 1920;
export const H = 1080;

// Decoded ring / polyline in unit Mercator with its bounding box (for culling).
export type Ring = {pts: Float64Array; x0: number; y0: number; x1: number; y1: number};

export const decode = (flat: number[], q: number): Ring => {
	const pts = new Float64Array(flat.length);
	let x0 = Infinity;
	let y0 = Infinity;
	let x1 = -Infinity;
	let y1 = -Infinity;
	for (let i = 0; i < flat.length; i += 2) {
		const x = flat[i] / q;
		const y = flat[i + 1] / q;
		pts[i] = x;
		pts[i + 1] = y;
		if (x < x0) x0 = x;
		if (x > x1) x1 = x;
		if (y < y0) y0 = y;
		if (y > y1) y1 = y;
	}
	return {pts, x0, y0, x1, y1};
};

export const decodeAll = (rings: number[][] | undefined, q: number): Ring[] => (rings ?? []).map((r) => decode(r, q));

// Screen transform of the current camera: sx = x * k + ox, sy = y * k + oy.
export type Xf = {k: number; ox: number; oy: number};
export const xfOf = (cam: View): Xf => {
	const k = W / cam.w;
	return {k, ox: W / 2 - cam.x * k, oy: H / 2 - cam.y * k};
};
export const toScreen = (xf: Xf, x: number, y: number): [number, number] => [x * xf.k + xf.ox, y * xf.k + xf.oy];

// Horizontal copies needed when the view crosses the antimeridian (x < 0 or x > 1).
export const wrapOffsets = (cam: View): number[] => {
	const out = [0];
	if (cam.x - cam.w / 2 < 0) out.push(-1);
	if (cam.x + cam.w / 2 > 1) out.push(1);
	return out;
};

const r1 = (v: number) => Math.round(v * 10) / 10;

// SVG path for rings in screen space: culled, with sub-pixel points dropped. Returns '' if nothing is visible.
export const pathOf = (rings: Ring[], xf: Xf, offsets: number[], closed: boolean, minPx = 0.8, margin = 60): string => {
	let d = '';
	for (const off of offsets) {
		const ox = xf.ox + off * xf.k;
		for (const r of rings) {
			if (r.x1 * xf.k + ox < -margin || r.x0 * xf.k + ox > W + margin) continue;
			if (r.y1 * xf.k + xf.oy < -margin || r.y0 * xf.k + xf.oy > H + margin) continue;
			const p = r.pts;
			const n = p.length;
			let lx = p[0] * xf.k + ox;
			let ly = p[1] * xf.k + xf.oy;
			let seg = `M${r1(lx)} ${r1(ly)}`;
			let count = 1;
			for (let i = 2; i < n; i += 2) {
				const x = p[i] * xf.k + ox;
				const y = p[i + 1] * xf.k + xf.oy;
				if (i < n - 2 && Math.abs(x - lx) + Math.abs(y - ly) < minPx) continue;
				seg += `L${r1(x)} ${r1(y)}`;
				lx = x;
				ly = y;
				count++;
			}
			if (count > 1 || !closed) d += closed ? seg + 'Z' : seg;
		}
	}
	return d;
};

// Each ring as its own path with its screen length (for "drawing" outlines with a dash offset).
export const ringPaths = (rings: Ring[], xf: Xf, offsets: number[], minPx = 0.8): {d: string; len: number}[] => {
	const out: {d: string; len: number}[] = [];
	for (const off of offsets) {
		const ox = xf.ox + off * xf.k;
		for (const r of rings) {
			if (r.x1 * xf.k + ox < -60 || r.x0 * xf.k + ox > W + 60 || r.y1 * xf.k + xf.oy < -60 || r.y0 * xf.k + xf.oy > H + 60) continue;
			const p = r.pts;
			let lx = p[0] * xf.k + ox;
			let ly = p[1] * xf.k + xf.oy;
			const fx = lx;
			const fy = ly;
			let d = `M${r1(lx)} ${r1(ly)}`;
			let len = 0;
			for (let i = 2; i < p.length; i += 2) {
				const x = p[i] * xf.k + ox;
				const y = p[i + 1] * xf.k + xf.oy;
				const step = Math.hypot(x - lx, y - ly);
				if (step < minPx && i < p.length - 2) continue;
				d += `L${r1(x)} ${r1(y)}`;
				len += step;
				lx = x;
				ly = y;
			}
			len += Math.hypot(fx - lx, fy - ly);
			if (len > 4) out.push({d: d + 'Z', len});
		}
	}
	return out;
};

// Polyline helpers for routes: cumulative length in unit space, and the drawn part up to fraction p.
export const cumulative = (pts: Float64Array): Float64Array => {
	const cum = new Float64Array(pts.length / 2);
	for (let i = 1; i < cum.length; i++) {
		cum[i] = cum[i - 1] + Math.hypot(pts[2 * i] - pts[2 * i - 2], pts[2 * i + 1] - pts[2 * i - 1]);
	}
	return cum;
};

export const partialLine = (pts: Float64Array, cum: Float64Array, p: number): {pts: number[]; head: [number, number]; angle: number} => {
	const total = cum[cum.length - 1];
	const target = total * Math.min(Math.max(p, 0), 1);
	const out: number[] = [pts[0], pts[1]];
	let i = 1;
	while (i < cum.length && cum[i] <= target) {
		out.push(pts[2 * i], pts[2 * i + 1]);
		i++;
	}
	let hx = out[out.length - 2];
	let hy = out[out.length - 1];
	let angle = 0;
	if (i < cum.length) {
		const segLen = cum[i] - cum[i - 1];
		const t = segLen > 0 ? (target - cum[i - 1]) / segLen : 0;
		const ax = pts[2 * i - 2];
		const ay = pts[2 * i - 1];
		hx = ax + (pts[2 * i] - ax) * t;
		hy = ay + (pts[2 * i + 1] - ay) * t;
		out.push(hx, hy);
		angle = Math.atan2(pts[2 * i + 1] - ay, pts[2 * i] - ax);
	} else if (cum.length > 1) {
		const n = cum.length - 1;
		angle = Math.atan2(pts[2 * n + 1] - pts[2 * n - 1], pts[2 * n] - pts[2 * n - 2]);
	}
	return {pts: out, head: [hx, hy], angle};
};

export const linePath = (pts: number[], xf: Xf, off = 0): string => {
	let d = '';
	let lx = NaN;
	let ly = NaN;
	for (let i = 0; i < pts.length; i += 2) {
		const x = pts[i] * xf.k + xf.ox + off * xf.k;
		const y = pts[i + 1] * xf.k + xf.oy;
		if (i > 0 && i < pts.length - 2 && Math.abs(x - lx) + Math.abs(y - ly) < 0.8) continue;
		d += `${i === 0 ? 'M' : 'L'}${r1(x)} ${r1(y)}`;
		lx = x;
		ly = y;
	}
	return d;
};

// Unit Mercator <-> lon/lat (true-size outlines are rotated on the sphere, then projected).
const MAX_LAT = 85.0511287798;
export const merc = (lon: number, lat: number): [number, number] => {
	const l = Math.max(-MAX_LAT, Math.min(MAX_LAT, lat));
	const s = Math.sin((l * Math.PI) / 180);
	return [(lon + 180) / 360, 0.5 - Math.log((1 + s) / (1 - s)) / (4 * Math.PI)];
};
export const unmerc = (x: number, y: number): [number, number] => [x * 360 - 180, (Math.atan(Math.sinh(Math.PI * (1 - 2 * y))) * 180) / Math.PI];

// Rotation on the unit sphere that carries `from` onto `to` (both lon/lat), applied by fraction t.
export const sphereMover = (from: [number, number], to: [number, number]) => {
	const vec = (lon: number, lat: number) => {
		const a = (lon * Math.PI) / 180;
		const b = (lat * Math.PI) / 180;
		return [Math.cos(b) * Math.cos(a), Math.cos(b) * Math.sin(a), Math.sin(b)];
	};
	const a = vec(from[0], from[1]);
	const b = vec(to[0], to[1]);
	let ax = a[1] * b[2] - a[2] * b[1];
	let ay = a[2] * b[0] - a[0] * b[2];
	let az = a[0] * b[1] - a[1] * b[0];
	const n = Math.hypot(ax, ay, az) || 1;
	ax /= n;
	ay /= n;
	az /= n;
	const angle = Math.acos(Math.max(-1, Math.min(1, a[0] * b[0] + a[1] * b[1] + a[2] * b[2])));
	return (lon: number, lat: number, t: number): [number, number] => {
		const v = vec(lon, lat);
		const th = angle * t;
		const c = Math.cos(th);
		const s = Math.sin(th);
		const dot = ax * v[0] + ay * v[1] + az * v[2];
		// Rodrigues' rotation formula
		const rx = v[0] * c + (ay * v[2] - az * v[1]) * s + ax * dot * (1 - c);
		const ry = v[1] * c + (az * v[0] - ax * v[2]) * s + ay * dot * (1 - c);
		const rz = v[2] * c + (ax * v[1] - ay * v[0]) * s + az * dot * (1 - c);
		return [(Math.atan2(ry, rx) * 180) / Math.PI, (Math.asin(Math.max(-1, Math.min(1, rz))) * 180) / Math.PI];
	};
};
