import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';
import {body, clamp01, colors, display, easeOut} from '../theme';
import type {SceneData} from '../types';

export const TitleCard: React.FC<{scene: SceneData}> = ({scene}) => {
	const frame = useCurrentFrame();
	const titleP = easeOut((frame - 6) / 22);
	const lineP = easeOut((frame - 14) / 26);
	const subP = easeOut((frame - 30) / 20);
	// Slow tracking drift so the card never feels frozen.
	const spacing = interpolate(frame, [0, scene.durationFrames], [10, 22], {extrapolateRight: 'clamp'});
	return (
		<AbsoluteFill style={{backgroundColor: colors.bg, justifyContent: 'center', alignItems: 'center'}}>
			<div style={{textAlign: 'center'}}>
				<div
					style={{
						fontFamily: display,
						fontSize: 250,
						color: colors.text,
						letterSpacing: spacing,
						lineHeight: 1,
						opacity: titleP,
						transform: `translateY(${(1 - titleP) * 50}px)`,
					}}
				>
					{scene.onScreenText}
				</div>
				<div style={{height: 6, margin: '26px auto', width: 560 * lineP, backgroundColor: colors.accent}} />
				{scene.subtitle ? (
					<div
						style={{
							fontFamily: body,
							fontWeight: 500,
							fontSize: 54,
							color: colors.muted,
							letterSpacing: 8,
							textTransform: 'uppercase',
							opacity: subP,
							transform: `translateY(${(1 - clamp01(subP)) * 24}px)`,
						}}
					>
						{scene.subtitle}
					</div>
				) : null}
			</div>
		</AbsoluteFill>
	);
};
