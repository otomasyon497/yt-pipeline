import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {body, clamp01, colors, display, easeOut, formatNumber} from '../theme';
import type {CountUp} from '../types';

// Lower-third label: slides in, holds, fades out. Numbers marked by the pipeline count up while it appears.
// In a Short (vertical frame) it is a big headline near the top; `instant` = the hook line, fully there from frame 0.
export const OnScreenText: React.FC<{text: string; countUp?: CountUp | null; delay?: number; hold?: number; instant?: boolean}> = ({
	text,
	countUp,
	delay = 14,
	hold = 96,
	instant = false,
}) => {
	const frame = useCurrentFrame();
	const {width, height} = useVideoConfig();
	const vertical = height > width;
	const inP = instant ? 1 : easeOut((frame - delay) / 12);
	const out = clamp01((frame - (delay + hold)) / 10);
	const opacity = inP * (1 - out);
	if (opacity <= 0) return null;
	let shown = text;
	if (countUp) {
		const t = easeOut((frame - delay - 4) / 22);
		shown = countUp.prefix + formatNumber(countUp.value * t, countUp) + countUp.suffix;
	}
	const bar = <div style={{width: vertical ? 12 : 10, backgroundColor: colors.accent, transform: `scaleY(${instant ? 1 : easeOut((frame - delay) / 8)})`}} />;
	if (vertical) {
		return (
			<AbsoluteFill style={{justifyContent: 'flex-start', alignItems: 'center', padding: '170px 60px 0'}}>
				<div
					style={{
						opacity,
						transform: `translateY(${interpolate(inP, [0, 1], [-36, 0])}px)`,
						display: 'flex',
						alignItems: 'stretch',
						maxWidth: 960,
						backgroundColor: 'rgba(8,10,18,0.8)',
						boxShadow: '0 6px 24px rgba(0,0,0,0.4)',
					}}
				>
					{bar}
					<div
						style={{
							padding: '18px 30px 10px',
							fontFamily: display,
							fontSize: 88,
							lineHeight: 1.0,
							letterSpacing: 2,
							color: colors.text,
							textAlign: 'center',
							fontVariantNumeric: 'tabular-nums',
						}}
					>
						{shown}
					</div>
				</div>
			</AbsoluteFill>
		);
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
				{bar}
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
