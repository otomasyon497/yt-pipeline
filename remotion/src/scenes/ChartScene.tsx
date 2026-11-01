import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {body, clamp01, colors, display, easeOut} from '../theme';
import type {ChartSpec} from '../types';

const W = 1920;
const H = 1080;
const REF = '#e5484d'; // reference lines (thresholds) read as a warning
const OTHER = '#5b6787'; // bars that are not highlighted

const Title: React.FC<{text: string | null | undefined; p: number}> = ({text, p}) =>
	text ? (
		<text x={150} y={160} fontFamily={display} fontSize={86} fill={colors.text} opacity={p} letterSpacing={3}>
			{text.toUpperCase()}
		</text>
	) : null;

// Everything stays above y ~ 880: captions sit at the bottom of the frame.
// 2,063 / 55.5 / 0.7: whole numbers from 100 up, one decimal below.
const num = (v: number) => (Math.abs(v) >= 100 ? Math.round(v) : Math.round(v * 10) / 10).toLocaleString('en-US');
const fmt = (v: number, unit: string) => `${num(v)}${unit}`;

const Source: React.FC<{text?: string | null; p: number}> = ({text, p}) =>
	text ? (
		<text x={150} y={250} fontFamily={body} fontWeight={500} fontSize={28} fill={colors.muted} opacity={p}>
			{`Source: ${text}`}
		</text>
	) : null;

const Bars: React.FC<{chart: ChartSpec; frame: number}> = ({chart, frame}) => {
	const refV = chart.ref ? chart.ref[0] : 0;
	const max = Math.max(...chart.data.map((d) => d[1]), refV, 1e-9);
	const left = 470;
	const barMax = 1180;
	const n = chart.data.length;
	const rowH = Math.min(120, 500 / n);
	const barH = rowH * 0.66;
	const top = 320 + (500 - rowH * n) / 2;
	const hi = chart.highlight ?? 0;
	return (
		<>
			{chart.data.map(([label, value], i) => {
				const p = easeOut((frame - 22 - i * 10) / 36);
				const w = (value / max) * barMax * p;
				const y = top + i * rowH;
				return (
					<g key={`${label}${i}`} opacity={clamp01((frame - 16 - i * 10) / 10)}>
						<text x={left - 30} y={y + barH * 0.72} fontFamily={body} fontWeight={700} fontSize={Math.min(44, rowH * 0.36)} fill={colors.text} textAnchor="end">
							{label}
						</text>
						<rect x={left} y={y} width={barMax} height={barH} fill={colors.panel} />
						<rect x={left} y={y} width={w} height={barH} fill={i === hi ? colors.accent : OTHER} />
						<text x={left + w + 24} y={y + barH * 0.74} fontFamily={display} fontSize={Math.min(74, rowH * 0.6)} fill={colors.text}>
							{fmt(value * p, chart.unit)}
						</text>
					</g>
				);
			})}
			{chart.ref ? (
				<g opacity={clamp01((frame - 40 - n * 10) / 14)}>
					<line x1={left + (refV / max) * barMax} y1={top - 30} x2={left + (refV / max) * barMax} y2={top + rowH * n} stroke={REF} strokeWidth={4} strokeDasharray="14 10" />
					<text x={left + (refV / max) * barMax + 14} y={top - 40} fontFamily={body} fontWeight={700} fontSize={32} fill={REF}>
						{chart.ref[1]}
					</text>
				</g>
			) : null}
		</>
	);
};

const Line: React.FC<{chart: ChartSpec; frame: number}> = ({chart, frame}) => {
	const n = chart.data.length;
	const xs = chart.data.map((_, i) => 260 + (i * 1400) / Math.max(n - 1, 1));
	const vals = chart.data.map((d) => d[1]);
	const lo = Math.min(...vals, chart.ref ? chart.ref[0] : vals[0], 0);
	const hi = Math.max(...vals, chart.ref ? chart.ref[0] : vals[0]);
	const yOf = (v: number) => 780 - ((v - lo) / Math.max(hi - lo, 1e-9)) * 430;
	const ys = vals.map(yOf);
	const pts = xs.map((x, i) => `${x},${ys[i]}`).join(' ');
	let len = 0;
	for (let i = 1; i < n; i++) len += Math.hypot(xs[i] - xs[i - 1], ys[i] - ys[i - 1]);
	const p = easeOut((frame - 20) / (40 + 10 * n));
	const hiIdx = chart.highlight ?? n - 1;
	const valueSize = n > 6 ? 44 : 56;
	return (
		<>
			{chart.unit.trim() ? (
				<text x={1720} y={250} fontFamily={body} fontWeight={600} fontSize={30} fill={colors.muted} textAnchor="end" opacity={clamp01((frame - 12) / 12)}>
					{chart.unit.trim()}
				</text>
			) : null}
			<line x1={200} y1={800} x2={1720} y2={800} stroke={colors.line} strokeWidth={3} />
			{chart.ref ? (
				<g opacity={clamp01((frame - 10) / 14)}>
					<line x1={200} y1={yOf(chart.ref[0])} x2={1720} y2={yOf(chart.ref[0])} stroke={REF} strokeWidth={4} strokeDasharray="14 10" />
					<text x={1720} y={yOf(chart.ref[0]) - 16} fontFamily={body} fontWeight={700} fontSize={32} fill={REF} textAnchor="end">
						{chart.ref[1]}
					</text>
				</g>
			) : null}
			<polyline points={pts} fill="none" stroke={colors.accent} strokeWidth={9} strokeLinejoin="round" strokeLinecap="round" strokeDasharray={len} strokeDashoffset={len * (1 - p)} />
			{chart.data.map(([label, value], i) => {
				const shown = clamp01((p * (n - 1) - (i - 0.2)) / 0.4);
				const big = i === hiIdx;
				return (
					<g key={`${label}${i}`} opacity={shown}>
						<circle cx={xs[i]} cy={ys[i]} r={big ? 17 : 12} fill={big ? colors.accent : colors.text} />
						<text x={xs[i]} y={ys[i] - 34} fontFamily={display} fontSize={big ? valueSize + 14 : valueSize} fill={colors.text} textAnchor="middle">
							{num(value)}
						</text>
						<text x={xs[i]} y={850} fontFamily={body} fontWeight={500} fontSize={34} fill={colors.muted} textAnchor="middle">
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
			<AbsoluteFill style={{background: 'radial-gradient(ellipse at 30% 20%, rgba(245,166,35,0.07), transparent 60%)'}} />
			<svg width={W} height={H} viewBox={`0 0 ${W} ${H}`}>
				<Title text={chart.title} p={easeOut((frame - 4) / 18)} />
				<rect x={150} y={190} width={220 * easeOut((frame - 8) / 24)} height={6} fill={colors.accent} />
				{chart.type === 'line' ? <Line chart={chart} frame={frame} /> : <Bars chart={chart} frame={frame} />}
				<Source text={chart.source} p={clamp01((frame - 30) / 16)} />
			</svg>
		</AbsoluteFill>
	);
};
