import React from 'react';
import {AbsoluteFill, Sequence, useCurrentFrame} from 'remotion';
import {Captions} from './components/Captions';
import {OnScreenText} from './components/OnScreenText';
import {MapBlock} from './map/MapBlock';
import {ChapterCard} from './scenes/ChapterCard';
import {ChartScene} from './scenes/ChartScene';
import {ImageScene} from './scenes/ImageScene';
import {PhotoScene} from './scenes/PhotoScene';
import {QuoteScene} from './scenes/QuoteScene';
import {StockScene} from './scenes/StockScene';
import {TitleCard} from './scenes/TitleCard';
import {colors, easeOut} from './theme';
import type {ShotData, Timeline} from './types';

const ShotBody: React.FC<{shot: ShotData}> = ({shot}) => {
	switch (shot.visual) {
		case 'stock':
			return <StockScene scene={shot} />;
		case 'ai_image':
			return <ImageScene scene={shot} />;
		case 'photo':
			return <PhotoScene scene={shot} />;
		case 'chart':
			return <ChartScene chart={shot.chart!} />;
		case 'map':
			return <MapBlock file={shot.media!} />;
		case 'title_card':
			return <TitleCard scene={shot} />;
		case 'quote':
			return <QuoteScene scene={shot} />;
		case 'chapter_card':
			return <ChapterCard shot={shot} />;
	}
};

// Every shot after the first appears over the previous one, which stays drawn for exactly that long
// (see timeline.py). Chapter cards punch in (scale down into place); everything else dissolves.
const ShotFrame: React.FC<{shot: ShotData; index: number}> = ({shot, index}) => {
	const frame = useCurrentFrame();
	const tin = Math.max(1, shot.transitionIn);
	const p = index === 0 ? 1 : Math.min(frame / tin, 1);
	const scale = shot.visual === 'chapter_card' && index > 0 ? 1.14 - 0.14 * easeOut(p) : 1;
	return (
		<AbsoluteFill style={{opacity: p, transform: scale !== 1 ? `scale(${scale})` : undefined, backgroundColor: colors.bg}}>
			<ShotBody shot={shot} />
			{shot.texts.map((t, k) => {
				const next = shot.texts[k + 1];
				const hold = Math.min(96, (next ? next.from : shot.durationFrames) - t.from - 14);
				return hold > 20 ? (
					<Sequence key={k} from={t.from} layout="none">
						<OnScreenText text={t.text} countUp={t.countUp} delay={0} hold={hold} />
					</Sequence>
				) : null;
			})}
		</AbsoluteFill>
	);
};

export const Episode: React.FC<Timeline> = ({shots, words, showCaptions}) => (
	<AbsoluteFill style={{backgroundColor: colors.bg}}>
		{shots.map((shot, i) => (
			<Sequence key={shot.id} from={shot.startFrame} durationInFrames={shot.durationFrames} layout="none">
				<ShotFrame shot={shot} index={i} />
			</Sequence>
		))}
		{showCaptions ? <Captions words={words} /> : null}
	</AbsoluteFill>
);
