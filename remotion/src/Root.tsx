import React from 'react';
import {Composition} from 'remotion';
import {Episode} from './Episode';
import {Thumbnail} from './Thumbnail';
import type {Timeline} from './types';

// Placeholder shown in Studio; real renders pass --props=<build>/timeline.json.
const emptyTimeline: Timeline = {fps: 24, width: 1920, height: 1080, totalFrames: 24, transitionFrames: 12, scenes: []};

export const RemotionRoot: React.FC = () => (
	<>
	<Composition
		id="Thumbnail"
		component={Thumbnail}
		durationInFrames={1}
		fps={30}
		width={1280}
		height={720}
		defaultProps={{text: 'Sample Title', background: 'thumb_A.jpg', layout: 'left' as const}}
	/>
	<Composition
		id="Episode"
		component={Episode}
		durationInFrames={emptyTimeline.totalFrames}
		fps={emptyTimeline.fps}
		width={emptyTimeline.width}
		height={emptyTimeline.height}
		defaultProps={emptyTimeline}
		calculateMetadata={({props}) => ({
			durationInFrames: props.totalFrames,
			fps: props.fps,
			width: props.width,
			height: props.height,
		})}
	/>
	</>
);
