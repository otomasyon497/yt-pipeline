import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {body, clamp01, colors, easeOut} from '../theme';

// Lower-third style label, shown near the start of a scene and then faded out.
export const OnScreenText: React.FC<{text: string; delay?: number; hold?: number}> = ({text, delay = 14, hold = 96}) => {
	const frame = useCurrentFrame();
	useVideoConfig();
	const inP = easeOut((frame - delay) / 14);
	const out = clamp01((frame - (delay + hold)) / 10);
	const opacity = inP * (1 - out);
	if (opacity <= 0) return null;
	return (
		<AbsoluteFill style={{justifyContent: 'flex-start', alignItems: 'flex-start', padding: '90px 110px'}}>
			<div
				style={{
					opacity,
					transform: `translateX(${interpolate(inP, [0, 1], [-40, 0])}px)`,
					display: 'flex',
					alignItems: 'stretch',
					backgroundColor: 'rgba(8,10,18,0.72)',
				}}
			>
				<div style={{width: 8, backgroundColor: colors.accent}} />
				<div style={{padding: '14px 28px', fontFamily: body, fontWeight: 700, fontSize: 44, color: colors.text, letterSpacing: 1}}>
					{text}
				</div>
			</div>
		</AbsoluteFill>
	);
};
