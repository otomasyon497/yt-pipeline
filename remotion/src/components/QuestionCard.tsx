import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {body, clamp01, colors, easeOut} from '../theme';

// Engagement question asked by the narrator: a comment card that slides in on the right
// (in a Short: drops in at the top centre, clear of YouTube's buttons on the right).
export const QuestionCard: React.FC<{text: string; hold: number}> = ({text, hold}) => {
	const frame = useCurrentFrame();
	const {width, height} = useVideoConfig();
	const vertical = height > width;
	const inP = easeOut(frame / 12);
	const out = clamp01((frame - hold) / 10);
	const opacity = inP * (1 - out);
	if (opacity <= 0) return null;
	return (
		<AbsoluteFill
			style={
				vertical
					? {justifyContent: 'flex-start', alignItems: 'center', padding: '170px 60px 0'}
					: {justifyContent: 'flex-start', alignItems: 'flex-end', padding: '96px 96px'}
			}
		>
			<div
				style={{
					opacity,
					transform: vertical ? `translateY(${interpolate(inP, [0, 1], [-40, 0])}px)` : `translateX(${interpolate(inP, [0, 1], [60, 0])}px)`,
					maxWidth: vertical ? 900 : 640,
					backgroundColor: 'rgba(8,10,18,0.84)',
					borderRadius: 18,
					padding: vertical ? '26px 34px 30px' : '22px 30px 26px',
					boxShadow: '0 10px 34px rgba(0,0,0,0.45)',
					borderLeft: `8px solid ${colors.accent}`,
				}}
			>
				<div style={{display: 'flex', alignItems: 'center', gap: 14, marginBottom: 10}}>
					{/* speech-bubble icon */}
					<svg width={vertical ? 42 : 34} height={vertical ? 37 : 30} viewBox="0 0 34 30">
						<path d="M4 2h26a3 3 0 0 1 3 3v15a3 3 0 0 1-3 3H14l-7 6v-6H4a3 3 0 0 1-3-3V5a3 3 0 0 1 3-3z" fill={colors.accent} />
					</svg>
					<div style={{fontFamily: body, fontWeight: 700, fontSize: vertical ? 30 : 24, letterSpacing: 3, color: colors.accent}}>TELL ME IN THE COMMENTS</div>
				</div>
				<div style={{fontFamily: body, fontWeight: 700, fontSize: vertical ? 58 : 44, lineHeight: 1.18, color: colors.text}}>{text}</div>
			</div>
		</AbsoluteFill>
	);
};
