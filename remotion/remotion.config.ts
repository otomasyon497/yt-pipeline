import {Config} from '@remotion/cli/config';

// Render defaults tuned for a 2-vCPU GitHub runner (also passed explicitly in the workflow).
Config.setVideoImageFormat('jpeg');
Config.setJpegQuality(88);
Config.setCodec('h264');
Config.setCrf(20);
Config.setX264Preset('veryfast');
Config.setConcurrency(2);
Config.setMuted(true); // audio is mixed with ffmpeg and muxed afterwards
Config.setOverwriteOutput(true);
