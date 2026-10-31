import React from 'react';
import {AbsoluteFill, Sequence, useCurrentFrame} from 'remotion';
import {Captions} from './components/Captions';
import {OnScreenText} from './components/OnScreenText';
import {ChapterCard} from './scenes/ChapterCard';
import {ChartScene} from './scenes/ChartScene';
import {ImageScene} from './scenes/ImageScene';
import {MapScene} from './scenes/MapScene';
import {QuoteScene} from './scenes/QuoteScene';
import {StockScene} from './scenes/StockScene';
import {TitleCard} from './scenes/TitleCard';
import {colors} from './theme';
import type {ShotData, Timeline} from './types';

const ShotBody: React.FC<{shot: ShotData}> = ({shot}) => {
	switch (shot.visual) {
		case 'stock':
			return <StockScene scene={shot} />;
		case 'ai_image':
			return <ImageScene scene={shot} />;
		case 'chart':
			return <ChartScene chart={shot.chart!} />;
		case 'map':
			return <MapScene map={shot.map!} duration={shot.durationFrames} />;
		case 'title_card':
			return <TitleCard scene={shot} />;
		case 'quote':
			return <QuoteScene scene={shot} />;
		case 'chapter_card':
			return <ChapterCard shot={shot} />;
	}
};

// Dissolve: every shot after the first fades in over `fade` frames on top of the previous one,
// which stays drawn for exactly that long (see timeline.py).
const ShotFrame: React.FC<{shot: ShotData; index: number; fade: number}> = ({shot, index, fade}) => {
	const frame = useCurrentFrame();
	const opacity = index === 0 ? 1 : Math.min(frame / fade, 1);
	const labelled = shot.visual === 'stock' || shot.visual === 'ai_image' || shot.visual === 'map';
	return (
		<AbsoluteFill style={{opacity, backgroundColor: colors.bg}}>
			<ShotBody shot={shot} />
			{labelled && shot.onScreenText ? <OnScreenText text={shot.onScreenText} delay={fade + 6} /> : null}
		</AbsoluteFill>
	);
};

export const Episode: React.FC<Timeline> = ({shots, words, transitionFrames, showCaptions}) => (
	<AbsoluteFill style={{backgroundColor: colors.bg}}>
		{shots.map((shot, i) => (
			<Sequence key={shot.id} from={shot.startFrame} durationInFrames={shot.durationFrames} layout="none">
				<ShotFrame shot={shot} index={i} fade={transitionFrames} />
			</Sequence>
		))}
		{showCaptions ? <Captions words={words} /> : null}
	</AbsoluteFill>
);
