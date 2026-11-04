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
// Decimals follow the data: 150.6 stays 150.6, whole-number series stay whole while they count up.
const decimalsOf = (chart: ChartSpec) => (chart.data.some(([, v]) => !Number.isInteger(v)) ? 1 : 0);
const num = (v: number, dec = 0) => {
	const d = Math.abs(v) >= 1000 ? 0 : dec;
	return (d ? Math.round(v * 10) / 10 : Math.round(v)).toLocaleString('en-US', {minimumFractionDigits: d, maximumFractionDigits: d});
};
const fmt = (v: number, unit: string, dec = 0) => `${num(v, dec)}${unit}`;

const Source: React.FC<{text?: string | null; p: number}> = ({text, p}) =>
	text ? (
		<text x={150} y={250} fontFamily={body} fontWeight={500} fontSize={28} fill={colors.muted} opacity={p}>
			{`Source: ${text}`}
		</text>
	) : null;

const Bars: React.FC<{chart: ChartSpec; frame: number}> = ({chart, frame}) => {
	const refV = chart.ref ? chart.ref[0] : 0;
	const max = Math.max(...chart.data.map((d) => d[1]), refV, 1e-9);
	const n = chart.data.length;
	const rowH = Math.min(120, 500 / n);
	const labelSize = Math.min(44, rowH * 0.36);
	// Labels sit right-aligned before the bars: make room for the longest one (Inter bold, ~0.56 em per glyph),
	// so "Caspian, lost since 1996" does not run off the left edge.
	const longestLabel = Math.max(...chart.data.map(([label]) => label.length));
	const left = Math.min(860, Math.max(470, 180 + longestLabel * labelSize * 0.56));
	const dec = decimalsOf(chart);
	// Leave room for the longest value label after the longest bar (display font ~0.5 em per glyph).
	const longest = Math.max(...chart.data.map(([, v]) => fmt(v, chart.unit, dec).length));
	const barMax = Math.min(1180, W - 120 - left - 24 - longest * Math.min(74, rowH * 0.6) * 0.5);
	const barH = rowH * 0.66;
	const top = 320 + (500 - rowH * n) / 2;
	const hi = chart.highlight ?? 0;
	const reveal = chart.reveal ?? [];
	const n0 = n - reveal.length; // items on screen from the start
	const t0 = (i: number) => (i < n0 ? 22 + i * 10 : reveal[i - n0]);
	return (
		<>
			{chart.data.map(([label, value], i) => {
				const p = easeOut((frame - t0(i)) / (i < n0 ? 36 : 28));
				const w = (value / max) * barMax * p;
				const y = top + i * rowH;
				return (
					<g key={`${label}${i}`} opacity={clamp01((frame - t0(i) + 6) / 10)}>
						<text x={left - 30} y={y + barH * 0.72} fontFamily={body} fontWeight={700} fontSize={labelSize} fill={colors.text} textAnchor="end">
							{label}
						</text>
						<rect x={left} y={y} width={barMax} height={barH} fill={colors.panel} />
						<rect x={left} y={y} width={w} height={barH} fill={i === hi ? colors.accent : OTHER} />
						<text x={left + w + 24} y={y + barH * 0.74} fontFamily={display} fontSize={Math.min(74, rowH * 0.6)} fill={colors.text}>
							{fmt(value * p, chart.unit, dec)}
						</text>
					</g>
				);
			})}
			{chart.ref ? (() => {
				const rx = left + (refV / max) * barMax;
				// A reference line near the longest bar sits close to the right edge: put its label on the left side of
				// the line when it would run out of the frame (Inter bold, ~0.56 em per glyph).
				const flip = rx + 14 + chart.ref[1].length * 32 * 0.56 > W - 60;
				return (
					<g opacity={clamp01((frame - 40 - n0 * 10) / 14)}>
						<line x1={rx} y1={top - 30} x2={rx} y2={top + rowH * n} stroke={REF} strokeWidth={4} strokeDasharray="14 10" />
						<text x={flip ? rx - 14 : rx + 14} y={top - 40} fontFamily={body} fontWeight={700} fontSize={32} fill={REF} textAnchor={flip ? 'end' : 'start'}>
							{chart.ref[1]}
						</text>
					</g>
				);
			})() : null}
		</>
	);
};

const Line: React.FC<{chart: ChartSpec; frame: number}> = ({chart, frame}) => {
	const n = chart.data.length;
	// Year labels (1929, 1977, 1995 ...) sit on a true time axis, so 48 years do not look as short as 5.
	const years = chart.data.map(([label]) => (/^\d{4}$/.test(label) ? Number(label) : NaN));
	const timeAxis = n > 2 && years.every((y, i) => !Number.isNaN(y) && (i === 0 || y > years[i - 1]));
	const xs = chart.data.map((_, i) =>
		260 + (timeAxis ? (years[i] - years[0]) / Math.max(years[n - 1] - years[0], 1) : i / Math.max(n - 1, 1)) * 1400,
	);
	const vals = chart.data.map((d) => d[1]);
	const minV = Math.min(...vals, chart.ref ? chart.ref[0] : vals[0]);
	const hi = Math.max(...vals, chart.ref ? chart.ref[0] : vals[0]);
	// Lines show change: values far from zero (e.g. lake levels 540-640 m, or -26 to -29 m below the ocean) get a
	// baseline just under the minimum; positive series that come close to zero start at zero.
	const lo = minV >= 0 && minV < 0.4 * hi ? 0 : minV - 0.15 * (hi - minV);
	const yOf = (v: number) => 780 - ((v - lo) / Math.max(hi - lo, 1e-9)) * 430;
	const ys = vals.map(yOf);
	const pts = xs.map((x, i) => `${x},${ys[i]}`).join(' ');
	const seg = xs.slice(1).map((x, i) => Math.hypot(x - xs[i], ys[i + 1] - ys[i]));
	const len = seg.reduce((a, b) => a + b, 0);
	const reveal = chart.reveal ?? [];
	const n0 = n - reveal.length; // points drawn by the opening animation
	let q = easeOut((frame - 20) / (40 + 10 * n0)) * (n0 - 1);
	reveal.forEach((f) => {
		q += easeOut((frame - f) / 24);
	});
	const whole = Math.min(Math.floor(q), n - 1);
	const drawn = seg.slice(0, whole).reduce((a, b) => a + b, 0) + (whole < n - 1 ? (q - whole) * seg[whole] : 0);
	const hiIdx = chart.highlight ?? n - 1;
	const valueSize = n > 6 ? 44 : 56;
	const dec = decimalsOf(chart);
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
					<text x={210} y={yOf(chart.ref[0]) + 44} fontFamily={body} fontWeight={700} fontSize={32} fill={REF}>
						{chart.ref[1]}
					</text>
				</g>
			) : null}
			<polyline points={pts} fill="none" stroke={colors.accent} strokeWidth={9} strokeLinejoin="round" strokeLinecap="round" strokeDasharray={len} strokeDashoffset={len - drawn} />
			{chart.data.map(([label, value], i) => {
				const shown = clamp01((q - (i - 0.2)) / 0.4);
				const big = i === hiIdx;
				return (
					<g key={`${label}${i}`} opacity={shown}>
						<circle cx={xs[i]} cy={ys[i]} r={big ? 17 : 12} fill={big ? colors.accent : colors.text} />
						<text x={xs[i]} y={ys[i] - 34} fontFamily={display} fontSize={big ? valueSize + 14 : valueSize} fill={colors.text} textAnchor="middle">
							{num(value, dec)}
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
