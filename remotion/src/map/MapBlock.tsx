import React, {useEffect, useMemo, useState} from 'react';
import {AbsoluteFill, Img, cancelRender, continueRender, delayRender, staticFile, useCurrentFrame} from 'remotion';
import {body, bodyItalic} from '../theme';
import {easeInOut, makeCamera, type View} from './camera';
import {
	H,
	W,
	cumulative,
	decode,
	decodeAll,
	linePath,
	merc,
	partialLine,
	pathOf,
	ringPaths,
	sphereMover,
	toScreen,
	wrapOffsets,
	xfOf,
	type Ring,
	type Xf,
} from './geometry';
import {Globe} from './Globe';
import {placeLabels, textWidth, type LabelReq, type Placement} from './labels';
import {STYLES, rampColor, type MapStyle} from './styles';
import type {ArrowEl, ChoroplethEl, HighlightEl, MapBlockData, MapElement, PlaceEl, RouteEl, TrueSizeEl} from './types';

const clamp01 = (t: number) => Math.min(Math.max(t, 0), 1);
const FADE = 8;
const life = (e: {in: number; out: number}, f: number) => clamp01((f - e.in) / FADE) * clamp01((e.out - f) / FADE);
const popIn = (age: number) => (age <= 0 ? 0 : age < 5 ? (age / 5) * 1.25 : age < 10 ? 1.25 - ((age - 5) / 5) * 0.25 : 1);
const compact = (v: number) => {
	const a = Math.abs(v);
	const [d, s] = a >= 1e12 ? [1e12, 'T'] : a >= 1e9 ? [1e9, 'B'] : a >= 1e6 ? [1e6, 'M'] : a >= 1e3 ? [1e3, 'K'] : [1, ''];
	const n = v / d;
	return `${n >= 100 || d === 1 ? Math.round(n) : n.toFixed(1)}${s}`;
};

// ------------------------------------------------------------------ data loading

const cache = new Map<string, MapBlockData>();

const useBlockData = (file: string): MapBlockData | null => {
	const [data, setData] = useState<MapBlockData | null>(cache.get(file) ?? null);
	const [handle] = useState(() => (cache.has(file) ? null : delayRender(`map block ${file}`)));
	useEffect(() => {
		if (data || handle === null) return;
		fetch(staticFile(`media/${file}`))
			.then((r) => r.json())
			.then((d: MapBlockData) => {
				cache.set(file, d);
				setData(d);
				continueRender(handle);
			})
			.catch((err) => cancelRender(err));
	}, [data, file, handle]);
	return data;
};

export const MapBlock: React.FC<{file: string}> = ({file}) => {
	const data = useBlockData(file);
	return data ? <MapView data={data} /> : null;
};

// ------------------------------------------------------------------ labels

type LabelEl = {id: string; el: MapElement; text: string; size: number; spacing: number; upper: boolean; italic: boolean; x: number; y: number; r: number; priority: number};

const labelsOf = (elements: MapElement[]): LabelEl[] => {
	const out: LabelEl[] = [];
	elements.forEach((el, i) => {
		const id = `${el.kind}${i}`;
		if (el.kind === 'highlight') {
			out.push({id, el, text: el.name, size: 32, spacing: 5, upper: true, italic: false, x: el.lx, y: el.ly, r: 0, priority: 0});
		} else if (el.kind === 'place' && el.label) {
			const sea = el.marker === 'sea';
			out.push({id, el, text: el.label, size: sea ? 27 : 30, spacing: sea ? 3 : 0.5, upper: false, italic: sea, x: el.x, y: el.y, r: sea ? 0 : 11, priority: sea ? 3 : 1});
		} else if (el.kind === 'route' && el.label) {
			const n = el.pts.length;
			out.push({id, el, text: el.label, size: 27, spacing: 0.5, upper: false, italic: false, x: el.pts[n - 2], y: el.pts[n - 1], r: 9, priority: 2});
		} else if (el.kind === 'arrow' && el.label) {
			out.push({id, el, text: el.label, size: 27, spacing: 0.5, upper: false, italic: false, x: el.from[0], y: el.from[1], r: 10, priority: 2});
		}
	});
	return out;
};

// ------------------------------------------------------------------ the map

const MapView: React.FC<{data: MapBlockData}> = ({data}) => {
	const frame = useCurrentFrame();
	const style: MapStyle = STYLES[data.style] ?? STYLES.satellite;
	const q = data.q;
	const camera = useMemo(() => makeCamera(data.cams, data.rho, data.drift, data.fps), [data]);

	// Decode everything once.
	const lods = useMemo(
		() =>
			data.lods.map((l) => ({
				...l,
				landR: decodeAll(l.land, q),
				lakesR: decodeAll(l.lakes, q),
				riversR: decodeAll(l.rivers, q),
				coastR: decodeAll(l.coast, q),
				bordersR: decodeAll(l.borders, q),
			})),
		[data, q],
	);
	const decoded = useMemo(
		() =>
			data.elements.map((el) => {
				if (el.kind === 'highlight') return {rings: decodeAll(el.rings, q)};
				if (el.kind === 'choropleth') return {items: el.items.map((it) => ({t: it.t, rings: decodeAll(it.rings, q)}))};
				if (el.kind === 'route') {
					const r = decode(el.pts, q);
					return {line: r.pts, cum: cumulative(r.pts)};
				}
				if (el.kind === 'truesize') return {mover: sphereMover(el.from, el.to)};
				return {};
			}),
		[data, q],
	);
	// Label anchors in unit coordinates (routes are stored as ints).
	const labelEls = useMemo(
		() =>
			labelsOf(data.elements).map((l) => (l.el.kind === 'route' ? {...l, x: l.x / q, y: l.y / q} : l)),
		[data, q],
	);

	// Label placement per "epoch" (camera arrivals and label appearances), kept stable between epochs.
	const epochs = useMemo(() => {
		const arrivalOf = (f: number) => {
			for (const k of data.cams) if (f > k.start && f < k.start + k.frames) return k.start + k.frames;
			return f;
		};
		const frames = Array.from(new Set([0, ...camera.arrivals, ...labelEls.map((l) => l.el.in)])).sort((a, b) => a - b);
		let prev = new Map<string, Placement>();
		return frames.map((f) => {
			const cam = camera.at(arrivalOf(f));
			const xf = xfOf(cam);
			const reqs: LabelReq[] = labelEls
				.filter((l) => l.el.in <= f && l.el.out > f + 4)
				.map((l) => {
					const [sx, sy] = toScreen(xf, l.x, l.y);
					return {id: l.id, x: sx, y: sy, w: textWidth(l.text, l.size, l.spacing, l.upper), h: l.size, r: l.r, priority: l.priority};
				});
			prev = placeLabels(reqs, data.safeBottom, prev);
			return {f, placements: prev};
		});
	}, [camera, labelEls, data]);

	const cam: View = camera.at(frame);
	const xf = xfOf(cam);
	const offsets = wrapOffsets(cam);
	const span = cam.w * 360;

	// Level of detail: the finest one that covers the view at this zoom.
	const halfH = (cam.w * H) / W / 2;
	const lod =
		lods.find(
			(l) =>
				span <= l.maxSpan * 1.3 &&
				l.box[0] <= cam.x - cam.w / 2 + 1e-9 &&
				l.box[2] >= cam.x + cam.w / 2 - 1e-9 &&
				l.box[1] <= Math.max(0, cam.y - halfH) + 1e-9 &&
				l.box[3] >= Math.min(1, cam.y + halfH) - 1e-9,
		) ?? lods[lods.length - 1];

	// Night lights crossfade.
	let night = 0;
	for (const ch of [...data.layers].sort((a, b) => a.f - b.f)) {
		if (frame < ch.f) break;
		const target = ch.layer === 'night' ? 1 : 0;
		const t = clamp01((frame - ch.f) / 18);
		night = night + (target - night) * t;
	}

	// Globe intro hides the flat map until it hands over.
	const globe = data.globe;
	const globeFade = globe ? 1 - clamp01((frame - (globe.frames - 10)) / 10) : 0;
	const flatHidden = globe !== null && globeFade >= 0.999;

	const epochIdx = (() => {
		let k = 0;
		for (let i = 0; i < epochs.length; i++) if (epochs[i].f <= frame) k = i;
		return k;
	})();
	const placement = (id: string): {p: Placement | undefined; vis: number} => {
		const cur = epochs[epochIdx]?.placements.get(id);
		const prev = epochIdx > 0 ? epochs[epochIdx - 1].placements.get(id) : undefined;
		const now = cur?.visible ? 1 : 0;
		const before = prev?.visible ? 1 : now;
		const blend = clamp01((frame - (epochs[epochIdx]?.f ?? 0)) / 6);
		return {p: cur ?? prev, vis: before + (now - before) * blend};
	};

	const visible = data.elements.map((el) => life(el, frame));
	const highlights = data.elements
		.map((el, i) => ({el, i}))
		.filter((x): x is {el: HighlightEl; i: number} => x.el.kind === 'highlight' && visible[x.i] > 0);
	const dimLevel = Math.max(0, ...highlights.filter((h) => h.el.dim).map((h) => visible[h.i]));

	const rasters = useMemo(
		() =>
			[...data.rasters].sort((a, b) => (a.layer === b.layer ? b.x1 - b.x0 - (a.x1 - a.x0) : a.layer === 'night' ? 1 : -1)),
		[data],
	);

	if (flatHidden && globe) {
		return <Globe spec={globe} style={style} frame={frame} endW={camera.at(globe.frames).w} fade={1} />;
	}

	return (
		<AbsoluteFill style={{backgroundColor: style.ocean, overflow: 'hidden'}}>
			{style.vector ? (
				<svg width={W} height={H} style={{position: 'absolute'}}>
					<path d={pathOf(lod.landR, xf, offsets, true)} fill={style.land} />
				</svg>
			) : null}
			{rasters.map((r, i) => {
				const [x0, y0] = toScreen(xf, r.x0, r.y0);
				const [x1, y1] = toScreen(xf, r.x1, r.y1);
				const onScreen = x1 > 0 && x0 < W && y1 > 0 && y0 < H;
				const layerOpacity = r.layer === 'night' ? night : r.layer === 'day' ? 1 : style.reliefOpacity;
				const opacity = onScreen ? layerOpacity : 0;
				return (
					<Img
						key={`${r.src}-${i}`}
						src={staticFile(`media/${r.src}`)}
						style={{
							position: 'absolute',
							left: x0,
							top: y0,
							width: x1 - x0,
							height: y1 - y0,
							opacity,
							filter: r.layer === 'relief' || style.rasterFilter === 'none' ? undefined : style.rasterFilter,
							mixBlendMode: r.layer === 'relief' ? 'soft-light' : 'normal',
						}}
					/>
				);
			})}
			<svg width={W} height={H} style={{position: 'absolute'}}>
				{style.vector ? (
					<>
						<path d={pathOf(lod.lakesR, xf, offsets, true)} fill={style.lake} />
						<path d={pathOf(lod.riversR, xf, offsets, false)} fill="none" stroke={style.river} strokeWidth={style.riverWidth} strokeLinejoin="round" />
					</>
				) : null}
				{data.elements.map((el, i) =>
					el.kind === 'choropleth' && visible[i] > 0 ? (
						<Choropleth key={i} el={el} items={(decoded[i] as {items: {t: number | null; rings: Ring[]}[]}).items} xf={xf} offsets={offsets} style={style} frame={frame} fade={visible[i]} />
					) : null,
				)}
				{dimLevel > 0 ? (
					<path
						d={`M0 0H${W}V${H}H0Z` + highlights.filter((h) => h.el.dim).map((h) => pathOf((decoded[h.i] as {rings: Ring[]}).rings, xf, offsets, true)).join('')}
						fill={style.dim}
						fillRule="evenodd"
						opacity={dimLevel}
					/>
				) : null}
				{highlights.map(({el, i}) => (
					<path
						key={`hf${i}`}
						d={pathOf((decoded[i] as {rings: Ring[]}).rings, xf, offsets, true)}
						fill={style.tints.accent}
						fillOpacity={style.highlightFill * visible[i] * (0.8 + 0.2 * Math.sin((frame - el.in) / 9))}
					/>
				))}
				{style.vector ? <path d={pathOf(lod.coastR, xf, offsets, false)} fill="none" stroke={style.coast} strokeWidth={style.coastWidth} strokeLinejoin="round" /> : null}
				<path d={pathOf(lod.bordersR, xf, offsets, false)} fill="none" stroke={style.border} strokeWidth={style.borderWidth} strokeLinejoin="round" />
				{highlights.map(({el, i}) => (
					<Outline key={`ho${i}`} rings={(decoded[i] as {rings: Ring[]}).rings} xf={xf} offsets={offsets} color={style.tints.accent} age={frame - el.in} fade={visible[i]} />
				))}
				{data.elements.map((el, i) =>
					el.kind === 'truesize' && visible[i] > 0 ? (
						<TrueSize key={i} el={el} mover={(decoded[i] as {mover: ReturnType<typeof sphereMover>}).mover} xf={xf} style={style} frame={frame} fade={visible[i]} />
					) : null,
				)}
				{data.elements.map((el, i) =>
					el.kind === 'route' && visible[i] > 0 ? (
						<Route key={i} el={el} line={(decoded[i] as {line: Float64Array; cum: Float64Array})} xf={xf} style={style} frame={frame} fade={visible[i]} />
					) : null,
				)}
				{data.elements.map((el, i) =>
					el.kind === 'arrow' && visible[i] > 0 ? <Arrow key={i} el={el} xf={xf} style={style} frame={frame} fade={visible[i]} /> : null,
				)}
				{data.elements.map((el, i) =>
					el.kind === 'place' && el.marker !== 'sea' && visible[i] > 0 ? <Marker key={i} el={el} xf={xf} style={style} frame={frame} fade={visible[i]} /> : null,
				)}
				{labelEls.map((l) => {
					const i = data.elements.indexOf(l.el);
					const fade = visible[i];
					if (fade <= 0) return null;
					if (l.el.kind === 'route') {
						const el = l.el as RouteEl;
						if (frame - el.in < el.draw * 0.85) return null; // label once the line has arrived
					}
					if (l.el.kind === 'arrow' && frame - l.el.in < 6) return null;
					const {p, vis} = placement(l.id);
					if (!p || vis <= 0) return null;
					const [sx, sy] = toScreen(xf, l.x, l.y);
					const color = l.el.kind === 'place' && (l.el as PlaceEl).marker === 'sea' ? style.seaLabel : style.label;
					return (
						<text
							key={l.id}
							x={sx + p.dx}
							y={sy + p.dy}
							textAnchor={p.anchor}
							fontFamily={l.italic ? bodyItalic : body}
							fontStyle={l.italic ? 'italic' : 'normal'}
							fontWeight={l.el.kind === 'highlight' ? 700 : l.italic ? 500 : 700}
							fontSize={l.size}
							letterSpacing={l.spacing}
							fill={color}
							stroke={style.labelHalo}
							strokeWidth={7}
							strokeLinejoin="round"
							paintOrder="stroke"
							opacity={fade * vis}
						>
							{l.upper ? l.text.toUpperCase() : l.text}
						</text>
					);
				})}
			</svg>
			{data.elements.map((el, i) => (el.kind === 'choropleth' && visible[i] > 0 ? <Legend key={i} el={el} style={style} fade={visible[i]} bottom={data.safeBottom} /> : null))}
			<AbsoluteFill
				style={{background: `radial-gradient(ellipse at center, rgba(0,0,0,0) 58%, rgba(0,0,0,${style.vignette}) 100%)`, pointerEvents: 'none'}}
			/>
			{globe && globeFade > 0 ? <Globe spec={globe} style={style} frame={frame} endW={camera.at(globe.frames).w} fade={globeFade} /> : null}
		</AbsoluteFill>
	);
};

// ------------------------------------------------------------------ overlay pieces

// Country outline that draws itself in, then breathes slightly.
const Outline: React.FC<{rings: Ring[]; xf: Xf; offsets: number[]; color: string; age: number; fade: number}> = ({rings, xf, offsets, color, age, fade}) => {
	const p = easeInOut(clamp01(age / 22));
	return (
		<g opacity={fade}>
			{ringPaths(rings, xf, offsets).map((r, k) => (
				<g key={k}>
					<path d={r.d} fill="none" stroke={color} strokeOpacity={0.28} strokeWidth={9} strokeLinejoin="round" strokeDasharray={`${r.len} ${r.len}`} strokeDashoffset={r.len * (1 - p)} />
					<path d={r.d} fill="none" stroke={color} strokeWidth={3} strokeLinejoin="round" strokeDasharray={`${r.len} ${r.len}`} strokeDashoffset={r.len * (1 - p)} />
				</g>
			))}
		</g>
	);
};

const Marker: React.FC<{el: PlaceEl; xf: Xf; style: MapStyle; frame: number; fade: number}> = ({el, xf, style, frame, fade}) => {
	const [x, y] = toScreen(xf, el.x, el.y);
	const s = popIn(frame - el.in);
	const accent = style.tints.accent;
	if (el.marker === 'event') {
		const pulse = ((frame - el.in) % 40) / 40;
		return (
			<g opacity={fade} transform={`translate(${x} ${y}) scale(${s})`}>
				<circle r={12 + pulse * 34} fill="none" stroke={accent} strokeWidth={3} opacity={1 - pulse} />
				<circle r={12 + ((pulse + 0.5) % 1) * 34} fill="none" stroke={accent} strokeWidth={3} opacity={1 - ((pulse + 0.5) % 1)} />
				<circle r={10} fill={accent} stroke={style.labelHalo} strokeWidth={3} />
			</g>
		);
	}
	if (el.marker === 'capital') {
		return (
			<g opacity={fade} transform={`translate(${x} ${y}) scale(${s})`}>
				<circle r={13} fill="none" stroke={style.label} strokeWidth={3} />
				<circle r={7} fill={style.label} stroke={style.labelHalo} strokeWidth={2} />
			</g>
		);
	}
	const fill = el.marker === 'city' ? style.label : accent;
	return (
		<g opacity={fade} transform={`translate(${x} ${y}) scale(${s})`}>
			<circle r={el.marker === 'city' ? 8 : 10} fill={fill} stroke={el.marker === 'city' ? style.labelHalo : '#ffffff'} strokeWidth={3} />
		</g>
	);
};

const Route: React.FC<{el: RouteEl; line: {line: Float64Array; cum: Float64Array}; xf: Xf; style: MapStyle; frame: number; fade: number}> = ({el, line, xf, style, frame, fade}) => {
	const p = easeInOut(clamp01((frame - el.in) / el.draw));
	const part = partialLine(line.line, line.cum, p);
	const d = linePath(part.pts, xf);
	const color = style.tints[el.tint];
	const [hx, hy] = toScreen(xf, part.head[0], part.head[1]);
	const dash = el.mode === 'air' ? '16 11' : undefined;
	return (
		<g opacity={fade}>
			<path d={d} fill="none" stroke={style.labelHalo} strokeOpacity={0.55} strokeWidth={10} strokeLinecap="round" strokeLinejoin="round" />
			<path d={d} fill="none" stroke={color} strokeOpacity={0.3} strokeWidth={14} strokeLinecap="round" strokeLinejoin="round" />
			<path d={d} fill="none" stroke={color} strokeWidth={5} strokeLinecap="round" strokeLinejoin="round" strokeDasharray={dash} />
			<circle cx={hx} cy={hy} r={p < 1 ? 9 : 8} fill={color} stroke="#ffffff" strokeWidth={3} />
		</g>
	);
};

const Arrow: React.FC<{el: ArrowEl; xf: Xf; style: MapStyle; frame: number; fade: number}> = ({el, xf, style, frame, fade}) => {
	const p = 1 - Math.pow(1 - clamp01((frame - el.in) / el.draw), 3);
	const [ax, ay] = toScreen(xf, el.from[0], el.from[1]);
	const [bx, by] = toScreen(xf, el.to[0], el.to[1]);
	const len = Math.hypot(bx - ax, by - ay);
	if (len < 4) return null;
	const cx = (ax + bx) / 2 - ((by - ay) / len) * el.bend * len;
	const cy = (ay + by) / 2 + ((bx - ax) / len) * el.bend * len;
	const pt = (t: number): [number, number] => [
		(1 - t) * (1 - t) * ax + 2 * (1 - t) * t * cx + t * t * bx,
		(1 - t) * (1 - t) * ay + 2 * (1 - t) * t * cy + t * t * by,
	];
	const head = Math.min(34, len * 0.3);
	const tEnd = Math.max(0.001, p * (1 - head / len / 1.2));
	let d = '';
	for (let k = 0; k <= 32; k++) {
		const [x, y] = pt((tEnd * k) / 32);
		d += `${k ? 'L' : 'M'}${x.toFixed(1)} ${y.toFixed(1)}`;
	}
	const [tx, ty] = pt(p);
	const [px, py] = pt(Math.max(0, p - 0.02));
	const ang = Math.atan2(ty - py, tx - px);
	const color = style.tints[el.tint];
	const tri = [
		[tx, ty],
		[tx - head * Math.cos(ang) + head * 0.55 * Math.sin(ang), ty - head * Math.sin(ang) - head * 0.55 * Math.cos(ang)],
		[tx - head * Math.cos(ang) - head * 0.55 * Math.sin(ang), ty - head * Math.sin(ang) + head * 0.55 * Math.cos(ang)],
	]
		.map(([x, y]) => `${x.toFixed(1)},${y.toFixed(1)}`)
		.join(' ');
	return (
		<g opacity={fade}>
			<path d={d} fill="none" stroke={style.labelHalo} strokeWidth={19} strokeLinecap="round" />
			<path d={d} fill="none" stroke={color} strokeWidth={13} strokeLinecap="round" />
			<polygon points={tri} fill={color} stroke={style.labelHalo} strokeWidth={3} strokeLinejoin="round" />
		</g>
	);
};

const TrueSize: React.FC<{el: TrueSizeEl; mover: ReturnType<typeof sphereMover>; xf: Xf; style: MapStyle; frame: number; fade: number}> = ({el, mover, xf, style, frame, fade}) => {
	const t = easeInOut(clamp01((frame - el.in) / el.move));
	let d = '';
	for (const flat of el.rings) {
		for (let i = 0; i < flat.length; i += 2) {
			const [lon, lat] = mover(flat[i], flat[i + 1], t);
			const [ux, uy] = merc(lon, lat);
			const [x, y] = toScreen(xf, ux, uy);
			d += `${i ? 'L' : 'M'}${x.toFixed(1)} ${y.toFixed(1)}`;
		}
		d += 'Z';
	}
	const [clon, clat] = mover(el.from[0], el.from[1], t);
	const [cx, cy] = toScreen(xf, ...merc(clon, clat));
	const accent = style.tints.accent;
	return (
		<g opacity={fade}>
			<path d={d} fill={accent} fillOpacity={0.55} stroke="#ffffff" strokeWidth={2.5} strokeLinejoin="round" />
			<text x={cx} y={cy + 10} textAnchor="middle" fontFamily={body} fontWeight={700} fontSize={30} letterSpacing={4} fill={style.label} stroke={style.labelHalo} strokeWidth={7} paintOrder="stroke">
				{el.label.toUpperCase()}
			</text>
		</g>
	);
};

const Choropleth: React.FC<{el: ChoroplethEl; items: {t: number | null; rings: Ring[]}[]; xf: Xf; offsets: number[]; style: MapStyle; frame: number; fade: number}> = ({
	el,
	items,
	xf,
	offsets,
	style,
	frame,
	fade,
}) => (
	<g>
		{items.map((it, k) => {
			const left = it.rings.length ? Math.min(...it.rings.map((r) => r.x0)) * xf.k + xf.ox : 0;
			const wave = clamp01((frame - el.in - (Math.max(0, Math.min(W, left)) / W) * 22) / 10); // sweeps west to east
			const d = pathOf(it.rings, xf, offsets, true);
			if (!d) return null;
			return (
				<path
					key={k}
					d={d}
					fill={it.t === null ? style.nodata : rampColor(style, it.t)}
					fillOpacity={(it.t === null ? 1 : style.choroplethOpacity) * wave * fade}
					stroke={style.labelHalo}
					strokeOpacity={0.35 * wave * fade}
					strokeWidth={0.8}
				/>
			);
		})}
	</g>
);

const Legend: React.FC<{el: ChoroplethEl; style: MapStyle; fade: number; bottom: number}> = ({el, style, fade, bottom}) => {
	const [a, b, c] = style.choropleth;
	return (
		<div
			style={{
				position: 'absolute',
				left: 70,
				bottom: bottom + 10,
				opacity: fade,
				backgroundColor: style.panel,
				padding: '18px 24px 16px',
				borderRadius: 10,
				fontFamily: body,
				color: style.label,
				minWidth: 380,
			}}
		>
			<div style={{fontWeight: 700, fontSize: 30}}>{el.title}</div>
			<div style={{height: 16, margin: '14px 0 8px', borderRadius: 3, background: `linear-gradient(90deg, ${a}, ${b}, ${c})`}} />
			<div style={{display: 'flex', justifyContent: 'space-between', fontWeight: 500, fontSize: 22}}>
				<span>
					{compact(el.min)}
					{el.unit}
				</span>
				<span>{el.scale === 'log' ? 'log scale' : ''}</span>
				<span>
					{compact(el.max)}
					{el.unit}
				</span>
			</div>
			{el.source ? <div style={{fontWeight: 500, fontSize: 18, opacity: 0.75, marginTop: 6}}>Source: {el.source}</div> : null}
		</div>
	);
};
