import React from 'react';
import {AbsoluteFill, Sequence, useCurrentFrame} from 'remotion';
import {Captions} from './components/Captions';
import {OnScreenText} from './components/OnScreenText';
import {ChartScene} from './scenes/ChartScene';
import {ImageScene} from './scenes/ImageScene';
import {MapScene} from './scenes/MapScene';
import {QuoteScene} from './scenes/QuoteScene';
import {StockScene} from './scenes/StockScene';
import {TitleCard} from './scenes/TitleCard';
import {colors} from './theme';
import type {SceneData, Timeline} from './types';

const SceneBody: React.FC<{scene: SceneData}> = ({scene}) => {
	switch (scene.visual) {
		case 'stock':
			return <StockScene scene={scene} />;
		case 'ai_image':
			return <ImageScene scene={scene} />;
		case 'chart':
			return <ChartScene chart={scene.chart!} />;
		case 'map':
			return <MapScene map={scene.map!} duration={scene.durationFrames} />;
		case 'title_card':
			return <TitleCard scene={scene} />;
		case 'quote':
			return <QuoteScene scene={scene} />;
	}
};

// Dissolve: every scene after the first fades in over `fade` frames on top of the previous one,
// which is kept on screen for exactly that long (see timeline.py).
const SceneFrame: React.FC<{scene: SceneData; index: number; fade: number}> = ({scene, index, fade}) => {
	const frame = useCurrentFrame();
	const opacity = index === 0 ? 1 : Math.min(frame / fade, 1);
	const labelled = scene.visual === 'stock' || scene.visual === 'ai_image' || scene.visual === 'map';
	return (
		<AbsoluteFill style={{opacity, backgroundColor: colors.bg}}>
			<SceneBody scene={scene} />
			{labelled && scene.onScreenText ? <OnScreenText text={scene.onScreenText} delay={fade + 8} /> : null}
			{scene.showCaptions ? <Captions words={scene.words} /> : null}
		</AbsoluteFill>
	);
};

export const Episode: React.FC<Timeline> = ({scenes, transitionFrames}) => (
	<AbsoluteFill style={{backgroundColor: colors.bg}}>
		{scenes.map((scene, i) => (
			<Sequence key={scene.id} from={scene.startFrame} durationInFrames={scene.durationFrames} layout="none">
				<SceneFrame scene={scene} index={i} fade={transitionFrames} />
			</Sequence>
		))}
	</AbsoluteFill>
);
