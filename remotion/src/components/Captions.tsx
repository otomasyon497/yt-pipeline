import React, {useMemo} from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {body, colors} from '../theme';
import type {Word} from '../types';

type Chunk = {words: Word[]; start: number; end: number};

// Group words into short on-screen phrases (max 6 words, break after punctuation).
const chunkWords = (words: Word[]): Chunk[] => {
	const chunks: Chunk[] = [];
	let cur: Word[] = [];
	const flush = () => {
		if (cur.length) chunks.push({words: cur, start: cur[0].start, end: cur[cur.length - 1].end});
		cur = [];
	};
	for (const w of words) {
		cur.push(w);
		if (cur.length >= 6 || (cur.length >= 3 && /[.,;:!?]$/.test(w.text))) flush();
	}
	flush();
	return chunks;
};

export const Captions: React.FC<{words: Word[]}> = ({words}) => {
	const frame = useCurrentFrame();
	const chunks = useMemo(() => chunkWords(words), [words]);

	// Show a phrase from its first word until the next phrase begins (or shortly after its last word).
	const idx = chunks.findIndex((c, i) => {
		const until = i + 1 < chunks.length ? chunks[i + 1].start : c.end + 8;
		return frame >= c.start && frame < until;
	});
	if (idx < 0) return null;
	const chunk = chunks[idx];

	return (
		<AbsoluteFill style={{justifyContent: 'flex-end', alignItems: 'center', paddingBottom: 70}}>
			<div
				style={{
					backgroundColor: 'rgba(8,10,18,0.72)',
					borderRadius: 14,
					padding: '14px 34px',
					fontFamily: body,
					fontWeight: 700,
					fontSize: 58,
					lineHeight: 1.2,
					maxWidth: 1560,
					textAlign: 'center',
				}}
			>
				{chunk.words.map((w, i) => {
					const active = frame >= w.start && frame < w.end;
					const spoken = frame >= w.end;
					return (
						<span
							key={i}
							style={{
								color: active ? colors.accent : spoken ? colors.text : 'rgba(244,241,234,0.62)',
								marginRight: i < chunk.words.length - 1 ? 14 : 0,
							}}
						>
							{w.text}
						</span>
					);
				})}
			</div>
		</AbsoluteFill>
	);
};
