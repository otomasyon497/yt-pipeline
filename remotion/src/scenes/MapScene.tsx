import React, {useMemo} from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {geoCentroid, geoNaturalEarth1, geoPath} from 'd3-geo';
import {feature} from 'topojson-client';
// Natural Earth data (public domain) packaged by world-atlas (ISC).
import topology from 'world-atlas/countries-110m.json';
import {body, clamp01, colors, easeOut} from '../theme';
import type {MapSpec} from '../types';

const W = 1920;
const H = 1080;

type Country = {name: string; d: string; bounds: [[number, number], [number, number]]; lonlat: [number, number]};

const projection = geoNaturalEarth1().fitExtent(
	[
		[60, 60],
		[W - 60, H - 60],
	],
	{type: 'Sphere'} as never,
);
const pathGen = geoPath(projection);

// Built once per bundle: path strings for every country (the per-frame work is just a transform).
const countries: Country[] = (feature(topology as never, (topology as never as {objects: {countries: never}}).objects.countries) as unknown as {
	features: {properties: {name: string}}[];
}).features.map((f) => ({
	name: f.properties.name,
	d: pathGen(f as never) ?? '',
	bounds: pathGen.bounds(f as never) as [[number, number], [number, number]],
	lonlat: geoCentroid(f as never) as [number, number],
}));

export const MapScene: React.FC<{map: MapSpec; duration: number}> = ({map, duration}) => {
	const frame = useCurrentFrame();
	const targets = useMemo(() => countries.filter((c) => map.highlight.includes(c.name)), [map.highlight]);

	// Camera: ease from the whole world to a box around the highlighted countries.
	let cx = W / 2;
	let cy = H / 2;
	let zoom = 1;
	if (targets.length) {
		const x0 = Math.min(...targets.map((t) => t.bounds[0][0]));
		const y0 = Math.min(...targets.map((t) => t.bounds[0][1]));
		const x1 = Math.max(...targets.map((t) => t.bounds[1][0]));
		const y1 = Math.max(...targets.map((t) => t.bounds[1][1]));
		const targetZoom = Math.min(7, 0.4 * Math.min(W / Math.max(x1 - x0, 1), H / Math.max(y1 - y0, 1)));
		const p = easeOut(frame / Math.max(duration * 0.75, 1));
		zoom = 1 + (targetZoom - 1) * p;
		cx = W / 2 + ((x0 + x1) / 2 - W / 2) * p;
		cy = H / 2 + ((y0 + y1) / 2 - H / 2) * p;
	}
	const fade = clamp01((frame - 10) / 24);

	return (
		<AbsoluteFill style={{backgroundColor: colors.bg}}>
			<svg width={W} height={H} viewBox={`0 0 ${W} ${H}`}>
				<g transform={`translate(${W / 2} ${H / 2}) scale(${zoom}) translate(${-cx} ${-cy})`}>
					{countries.map((c) => {
						const hot = map.highlight.includes(c.name);
						return (
							<path
								key={c.name}
								d={c.d}
								fill={hot ? colors.accent : colors.panel}
								fillOpacity={hot ? 0.35 + 0.65 * fade : 1}
								stroke={hot ? colors.accent : colors.line}
								strokeWidth={1.2}
								vectorEffect="non-scaling-stroke"
							/>
						);
					})}
					{map.points.map((pt) => {
						const xy = projection([pt.lon, pt.lat]);
						if (!xy) return null;
						const pulse = (frame % 36) / 36;
						return (
							<g key={pt.label} opacity={fade}>
								<circle cx={xy[0]} cy={xy[1]} r={(7 + pulse * 22) / zoom} fill="none" stroke={colors.text} strokeWidth={2} opacity={1 - pulse} vectorEffect="non-scaling-stroke" />
								<circle cx={xy[0]} cy={xy[1]} r={6 / zoom} fill={colors.text} />
								<text x={xy[0] + 14 / zoom} y={xy[1] - 12 / zoom} fontFamily={body} fontWeight={700} fontSize={26 / zoom} fill={colors.text}>
									{pt.label}
								</text>
							</g>
						);
					})}
				</g>
			</svg>
		</AbsoluteFill>
	);
};
