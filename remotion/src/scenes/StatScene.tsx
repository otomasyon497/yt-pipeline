import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {body, clamp01, colors, display, easeOut, formatNumber} from '../theme';
import type {StatSpec} from '../types';

// One big number on its own screen: the figure counts up, an accent bar draws under it, then the label, the note
// and the source fade in. Everything stays above y ~ 880 (captions).
export const StatScene: React.FC<{stat: StatSpec}> = ({stat}) => {
	const frame = useCurrentFrame();
	const c = stat.countUp;
	const t = easeOut((frame - 10) / 30);
	const shown = c ? c.prefix + formatNumber(c.value * t, c) + c.suffix : stat.value;
	// Bebas Neue is about 0.42 em per glyph: shrink long figures so they stay inside 1620 px.
	const size = Math.min(300, Math.floor(1620 / Math.max(1, stat.value.length * 0.42)));
	const labelP = easeOut((frame - 30) / 16);
	const noteP = easeOut((frame - 44) / 16);
	return (
		<AbsoluteFill style={{backgroundColor: colors.bg}}>
			<AbsoluteFill style={{background: 'radial-gradient(ellipse at 25% 30%, rgba(245,166,35,0.10), transparent 60%)'}} />
			<AbsoluteFill style={{justifyContent: 'center', padding: '0 150px 140px'}}>
				<div
					style={{
						fontFamily: display,
						fontSize: size,
						lineHeight: 0.9,
						letterSpacing: 4,
						color: colors.accent,
						fontVariantNumeric: 'tabular-nums',
						opacity: clamp01((frame - 4) / 8),
					}}
				>
					{shown}
				</div>
				<div style={{height: 10, width: 420, marginTop: 18, backgroundColor: colors.accent, transformOrigin: 'left', transform: `scaleX(${easeOut((frame - 16) / 22)})`}} />
				<div style={{marginTop: 34, fontFamily: body, fontWeight: 700, fontSize: 58, lineHeight: 1.2, color: colors.text, opacity: labelP, maxWidth: 1500}}>
					{stat.label}
				</div>
				{stat.note ? (
					<div style={{marginTop: 16, fontFamily: body, fontWeight: 500, fontSize: 42, lineHeight: 1.25, color: colors.muted, opacity: noteP, maxWidth: 1500}}>
						{stat.note}
					</div>
				) : null}
			</AbsoluteFill>
			{stat.source ? (
				<div style={{position: 'absolute', left: 150, top: 860, fontFamily: body, fontWeight: 500, fontSize: 28, color: colors.muted, opacity: noteP}}>
					{`Source: ${stat.source}`}
				</div>
			) : null}
		</AbsoluteFill>
	);
};
