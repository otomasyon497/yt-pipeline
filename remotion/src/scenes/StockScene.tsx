import React from 'react';
import {AbsoluteFill, staticFile} from 'remotion';
import {Video} from '@remotion/media';
import type {ShotData} from '../types';

// The clip is pre-trimmed/looped to exactly this scene's length by the Python pipeline.
export const StockScene: React.FC<{scene: ShotData}> = ({scene}) => (
	<AbsoluteFill style={{backgroundColor: '#000'}}>
		<Video src={staticFile(`media/${scene.media}`)} muted objectFit="cover" />
		{/* Flat dark wash keeps captions readable (no gradient/blur: slow on CPU renderers). */}
		<AbsoluteFill style={{backgroundColor: 'rgba(0,0,0,0.18)'}} />
	</AbsoluteFill>
);
