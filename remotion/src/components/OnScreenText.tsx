import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';
import {body, clamp01, colors, easeOut} from '../theme';
import type {CountUp} from '../types';

const formatNumber = (v: number, c: CountUp) => {
	const fixed = v.toFixed(c.decimals);
	if (!c.commas) return fixed;
	const [int, dec] = fixed.split('.');
	return int.replace(/\B(?=(\d{3})+(?!\d))/g, ',') + (dec ? `.${dec}` : '');
};

// Lower-third label: slides in, holds, fades out. Numbers marked by the pipeline count up while it appears.
export const OnScreenText: React.FC<{text: string; countUp?: CountUp | null; delay?: number; hold?: number}> = ({
	text,
	countUp,
	delay = 14,
	hold = 96,
}) => {
	const frame = useCurrentFrame();
	const inP = easeOut((frame - delay) / 12);
	const out = clamp01((frame - (delay + hold)) / 10);
	const opacity = inP * (1 - out);
	if (opacity <= 0) return null;
	let shown = text;
	if (countUp) {
		const t = easeOut((frame - delay - 4) / 22);
		shown = countUp.prefix + formatNumber(countUp.value * t, countUp) + countUp.suffix;
	}
	return (
		<AbsoluteFill style={{justifyContent: 'flex-start', alignItems: 'flex-start', padding: '86px 104px'}}>
			<div
				style={{
					opacity,
					transform: `translateX(${interpolate(inP, [0, 1], [-48, 0])}px)`,
					display: 'flex',
					alignItems: 'stretch',
					backgroundColor: 'rgba(8,10,18,0.78)',
					boxShadow: '0 6px 24px rgba(0,0,0,0.35)',
				}}
			>
				<div style={{width: 10, backgroundColor: colors.accent, transform: `scaleY(${easeOut((frame - delay) / 8)})`}} />
				<div
					style={{
						padding: '14px 30px',
						fontFamily: body,
						fontWeight: 700,
						fontSize: 48,
						color: colors.text,
						letterSpacing: 1,
						fontVariantNumeric: 'tabular-nums',
					}}
				>
					{shown}
				</div>
			</div>
		</AbsoluteFill>
	);
};
