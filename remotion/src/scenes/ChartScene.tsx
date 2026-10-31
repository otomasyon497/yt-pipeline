import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {body, clamp01, colors, display, easeOut} from '../theme';
import type {ChartSpec} from '../types';

const W = 1920;
const H = 1080;

const Title: React.FC<{text: string | null; p: number}> = ({text, p}) =>
	text ? (
		<text x={150} y={160} fontFamily={display} fontSize={86} fill={colors.text} opacity={p} letterSpacing={3}>
			{text.toUpperCase()}
		</text>
	) : null;

const fmt = (v: number, unit: string) => `${Math.round(v * 10) / 10}${unit}`;

const Bars: React.FC<{chart: ChartSpec; frame: number}> = ({chart, frame}) => {
	const max = Math.max(...chart.data.map((d) => d[1]), 1);
	const left = 420;
	const barMax = 1280;
	const rowH = 130;
	const top = 300;
	return (
		<>
			{chart.data.map(([label, value], i) => {
				const p = easeOut((frame - 22 - i * 10) / 36);
				const w = (value / max) * barMax * p;
				const y = top + i * rowH;
				return (
					<g key={label}>
						<text x={left - 30} y={y + 62} fontFamily={body} fontWeight={700} fontSize={44} fill={colors.text} textAnchor="end">
							{label}
						</text>
						<rect x={left} y={y} width={barMax} height={84} fill={colors.panel} />
						<rect x={left} y={y} width={w} height={84} fill={i === 0 ? colors.accent : colors.line} />
						<text x={left + w + 24} y={y + 60} fontFamily={display} fontSize={74} fill={colors.text}>
							{fmt(value * p, chart.unit)}
						</text>
					</g>
				);
			})}
		</>
	);
};

const Line: React.FC<{chart: ChartSpec; frame: number}> = ({chart, frame}) => {
	const xs = chart.data.map((_, i) => 240 + (i * 1440) / Math.max(chart.data.length - 1, 1));
	const vals = chart.data.map((d) => d[1]);
	const lo = Math.min(...vals, 0);
	const hi = Math.max(...vals);
	const ys = vals.map((v) => 880 - ((v - lo) / Math.max(hi - lo, 1e-9)) * 520);
	const pts = xs.map((x, i) => `${x},${ys[i]}`).join(' ');
	let len = 0;
	for (let i = 1; i < xs.length; i++) len += Math.hypot(xs[i] - xs[i - 1], ys[i] - ys[i - 1]);
	const p = easeOut((frame - 20) / 70);
	return (
		<>
			<line x1={200} y1={900} x2={1720} y2={900} stroke={colors.line} strokeWidth={3} />
			<polyline points={pts} fill="none" stroke={colors.accent} strokeWidth={9} strokeLinejoin="round" strokeDasharray={len} strokeDashoffset={len * (1 - p)} />
			{chart.data.map(([label, value], i) => {
				const shown = clamp01((p * (xs.length - 1) - (i - 0.2)) / 0.4);
				return (
					<g key={label} opacity={shown}>
						<circle cx={xs[i]} cy={ys[i]} r={13} fill={colors.text} />
						<text x={xs[i]} y={ys[i] - 34} fontFamily={display} fontSize={56} fill={colors.text} textAnchor="middle">
							{fmt(value, chart.unit)}
						</text>
						<text x={xs[i]} y={950} fontFamily={body} fontWeight={500} fontSize={34} fill={colors.muted} textAnchor="middle">
							{label}
						</text>
					</g>
				);
			})}
		</>
	);
};

export const ChartScene: React.FC<{chart: ChartSpec}> = ({chart}) => {
	const frame = useCurrentFrame();
	return (
		<AbsoluteFill style={{backgroundColor: colors.bg}}>
			<svg width={W} height={H} viewBox={`0 0 ${W} ${H}`}>
				<Title text={chart.title} p={easeOut((frame - 4) / 18)} />
				<rect x={150} y={190} width={220 * easeOut((frame - 8) / 24)} height={6} fill={colors.accent} />
				{chart.type === 'line' ? <Line chart={chart} frame={frame} /> : <Bars chart={chart} frame={frame} />}
			</svg>
		</AbsoluteFill>
	);
};
