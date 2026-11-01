import React from 'react';
import {AbsoluteFill, interpolate, staticFile, useCurrentFrame} from 'remotion';
import {Video} from '@remotion/media';
import type {ShotData} from '../types';

// The clip is pre-trimmed/looped to exactly this scene's length by the Python pipeline.
// A slow push-in keeps even static footage moving.
export const StockScene: React.FC<{scene: ShotData}> = ({scene}) => {
	const frame = useCurrentFrame();
	const zoom = interpolate(frame, [0, scene.durationFrames], [1, 1.06], {extrapolateRight: 'clamp'});
	return (
		<AbsoluteFill style={{backgroundColor: '#000', overflow: 'hidden'}}>
			<AbsoluteFill style={{transform: `scale(${zoom})`}}>
				<Video src={staticFile(`media/${scene.media}`)} muted objectFit="cover" />
			</AbsoluteFill>
			{/* Flat dark wash keeps captions readable (no gradient/blur: slow on CPU renderers). */}
			<AbsoluteFill style={{backgroundColor: 'rgba(0,0,0,0.18)'}} />
		</AbsoluteFill>
	);
};
