import React, {useEffect, useLayoutEffect, useMemo, useRef, useState} from 'react';
import {AbsoluteFill, cancelRender, continueRender, delayRender, staticFile} from 'remotion';
import {geoArea, geoGraticule10, geoOrthographic, geoPath} from 'd3-geo';
import {easeInOut} from './camera';
import {H, W} from './geometry';
import type {MapStyle} from './styles';
import type {GlobeSpec} from './types';

type Texture = {data: Uint8ClampedArray; w: number; h: number};
const textures = new Map<string, Texture>();

// Loads the equirectangular texture once per render tab and keeps its pixels.
const useTexture = (src: string | null): Texture | null => {
	const [tex, setTex] = useState<Texture | null>(src ? textures.get(src) ?? null : null);
	const [handle] = useState(() => (src && !textures.has(src) ? delayRender(`globe texture ${src}`) : null));
	useEffect(() => {
		if (!src || tex || handle === null) return;
		const img = new Image();
		img.crossOrigin = 'anonymous';
		img.onload = () => {
			const c = document.createElement('canvas');
			c.width = img.naturalWidth;
			c.height = img.naturalHeight;
			const ctx = c.getContext('2d', {willReadFrequently: true});
			if (!ctx) return cancelRender(new Error('no 2d context for the globe texture'));
			ctx.drawImage(img, 0, 0);
			const t = {data: ctx.getImageData(0, 0, c.width, c.height).data, w: c.width, h: c.height};
			textures.set(src, t);
			setTex(t);
			continueRender(handle);
		};
		img.onerror = () => cancelRender(new Error(`globe texture failed to load: ${src}`));
		img.src = staticFile(`media/${src}`);
	}, [src, tex, handle]);
	return tex;
};

// Satellite globe: inverse orthographic projection per pixel, at half resolution (it is moving fast).
const RasterGlobe: React.FC<{tex: Texture; lon: number; lat: number; r: number}> = ({tex, lon, lat, r}) => {
	const ref = useRef<HTMLCanvasElement>(null);
	const cw = W / 2;
	const ch = H / 2;
	useLayoutEffect(() => {
		const ctx = ref.current?.getContext('2d');
		if (!ctx) return;
		const out = ctx.createImageData(cw, ch);
		const o = out.data;
		const R = r / 2;
		const l0 = (lon * Math.PI) / 180;
		const p0 = (lat * Math.PI) / 180;
		const [cl, sl, cp, sp] = [Math.cos(l0), Math.sin(l0), Math.cos(p0), Math.sin(p0)];
		// screen axes on the sphere: east, north, towards the viewer
		const e = [-sl, cl, 0];
		const n = [-sp * cl, -sp * sl, cp];
		const c = [cp * cl, cp * sl, sp];
		const cx = cw / 2;
		const cy = ch / 2;
		const yMin = Math.max(0, Math.floor(cy - R));
		const yMax = Math.min(ch, Math.ceil(cy + R));
		const {data, w: tw, h: th} = tex;
		for (let py = yMin; py < yMax; py++) {
			const y = (cy - py - 0.5) / R;
			const span = Math.sqrt(Math.max(0, 1 - y * y));
			const xMin = Math.max(0, Math.floor(cx - span * R));
			const xMax = Math.min(cw, Math.ceil(cx + span * R));
			for (let px = xMin; px < xMax; px++) {
				const x = (px + 0.5 - cx) / R;
				const rho2 = x * x + y * y;
				if (rho2 >= 1) continue;
				const z = Math.sqrt(1 - rho2);
				const vx = x * e[0] + y * n[0] + z * c[0];
				const vy = x * e[1] + y * n[1] + z * c[1];
				const vz = x * e[2] + y * n[2] + z * c[2];
				const u = Math.floor(((Math.atan2(vy, vx) + Math.PI) / (2 * Math.PI)) * tw) % tw;
				const v = Math.min(th - 1, Math.floor(((Math.PI / 2 - Math.asin(vz)) / Math.PI) * th));
				const ti = (v * tw + u) * 4;
				const shade = 0.42 + 0.58 * Math.pow(z, 0.55);
				const oi = (py * cw + px) * 4;
				o[oi] = data[ti] * shade;
				o[oi + 1] = data[ti + 1] * shade;
				o[oi + 2] = data[ti + 2] * shade;
				o[oi + 3] = 255;
			}
		}
		ctx.putImageData(out, 0, 0);
	});
	return <canvas ref={ref} width={cw} height={ch} style={{position: 'absolute', left: 0, top: 0, width: W, height: H}} />;
};

// Globe intro: spins from (fromLon, fromLat) to the first view's centre while diving in, then fades out
// over the flat map, whose scale it matches at the end.
export const Globe: React.FC<{spec: GlobeSpec; style: MapStyle; frame: number; endW: number; fade: number}> = ({spec, style, frame, endW, fade}) => {
	const tex = useTexture(spec.texture);
	const land = useMemo(() => {
		const polys = spec.land.map((flat) => {
			const ring: [number, number][] = [];
			for (let i = 0; i < flat.length; i += 2) ring.push([flat[i], flat[i + 1]]);
			let poly = {type: 'Polygon' as const, coordinates: [ring]};
			// d3-geo wants clockwise exterior rings; flip any ring that would cover most of the sphere.
			if (geoArea(poly) > 2 * Math.PI) poly = {type: 'Polygon' as const, coordinates: [[...ring].reverse()]};
			return poly.coordinates;
		});
		return {type: 'MultiPolygon' as const, coordinates: polys};
	}, [spec.land]);
	const graticule = useMemo(() => geoGraticule10(), []);

	const t = easeInOut(Math.min(1, Math.max(0, frame / spec.frames)));
	const lon = spec.fromLon + (spec.toLon - spec.fromLon) * t;
	const lat = spec.fromLat + (spec.toLat - spec.fromLat) * t;
	const r0 = H * 0.4;
	const r1 = W / endW / (2 * Math.PI * Math.cos((spec.toLat * Math.PI) / 180));
	const r = r0 * Math.pow(r1 / r0, t);
	const projection = geoOrthographic().rotate([-lon, -lat]).scale(r).translate([W / 2, H / 2]).clipAngle(90);
	const path = geoPath(projection);
	const glow = Math.max(0, 1 - (r - r0) / (r0 * 1.5));
	return (
		<AbsoluteFill style={{opacity: fade, backgroundColor: '#02050c'}}>
			{/* atmosphere halo */}
			<div
				style={{
					position: 'absolute',
					left: W / 2 - r * 1.12,
					top: H / 2 - r * 1.12,
					width: r * 2.24,
					height: r * 2.24,
					borderRadius: '50%',
					background: `radial-gradient(circle, rgba(0,0,0,0) 86%, ${style.atmosphere} 89.5%, rgba(0,0,0,0) 100%)`,
					opacity: 0.35 + 0.65 * glow,
				}}
			/>
			{tex ? (
				<RasterGlobe tex={tex} lon={lon} lat={lat} r={r} />
			) : (
				<svg width={W} height={H} style={{position: 'absolute'}}>
					<path d={path({type: 'Sphere'}) ?? ''} fill={style.globeOcean} />
					<path d={path(graticule) ?? ''} fill="none" stroke="rgba(255,255,255,0.08)" strokeWidth={1} />
					<path d={path(land) ?? ''} fill={style.globeLand} stroke={style.coast} strokeWidth={1} />
				</svg>
			)}
			{/* terminator-style shading over the vector globe */}
			{!tex ? (
				<div
					style={{
						position: 'absolute',
						left: W / 2 - r,
						top: H / 2 - r,
						width: r * 2,
						height: r * 2,
						borderRadius: '50%',
						background: 'radial-gradient(circle at 40% 35%, rgba(255,255,255,0.06) 0%, rgba(0,0,0,0) 45%, rgba(0,0,0,0.45) 100%)',
					}}
				/>
			) : null}
		</AbsoluteFill>
	);
};
