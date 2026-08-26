#!/usr/bin/env node

import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import { mkdir, readdir } from 'node:fs/promises';
import path from 'node:path';
import process from 'node:process';

const execFileAsync = promisify(execFile);
const contentDirectory = path.resolve(import.meta.dirname, '..');
const sourceDirectory = path.join(contentDirectory, 'covers');
const outputDirectory = path.join(contentDirectory, 'thumbnails');
const supportedExtensions = new Set(['.jpg', '.jpeg', '.png', '.webp']);

async function runMagick(argumentsList) {
  return execFileAsync('magick', argumentsList, { maxBuffer: 1024 * 1024 });
}

async function alphaCrop(sourcePath) {
  const { stdout: sourceInfo } = await runMagick(['identify', '-format', '%w %h %[channels]', sourcePath]);
  const [widthText, heightText, channels] = sourceInfo.trim().split(/\s+/, 3);
  const width = Number(widthText);
  const height = Number(heightText);
  const opaqueLandscapeCrop = () => width / height > 1 ? `${Math.round(height * 2 / 3)}x${height}+0+0` : null;
  if (!channels.toLowerCase().includes('a')) return { crop: opaqueLandscapeCrop(), removeAlpha: false };

  const { stdout } = await runMagick([
    sourcePath,
    '-alpha', 'extract',
    '-threshold', '0',
    '-trim',
    '-format', '%wx%h%O',
    'info:'
  ]);
  const match = stdout.trim().match(/^(\d+)x(\d+)([+-]\d+)([+-]\d+)$/);
  // Some source exports contain artwork in RGB channels but set every alpha value
  // to zero. Preserve the artwork by explicitly removing that unusable alpha channel.
  if (!match || match[1] === '0' || match[2] === '0' || (match[1] === '1' && match[2] === '1' && match[3] === '-1' && match[4] === '-1')) {
    return { crop: opaqueLandscapeCrop(), removeAlpha: true };
  }
  return { crop: `${match[1]}x${match[2]}${match[3]}${match[4]}`, removeAlpha: false };
}

async function generateThumbnail(sourceName) {
  const sourcePath = path.join(sourceDirectory, sourceName);
  const outputName = `${path.basename(sourceName, path.extname(sourceName))}.webp`;
  const outputPath = path.join(outputDirectory, outputName);
  const { crop, removeAlpha } = await alphaCrop(sourcePath);
  const argumentsList = [sourcePath];
  if (crop) argumentsList.push('-crop', crop, '+repage');
  if (removeAlpha) argumentsList.push('-alpha', 'off');
  argumentsList.push('-resize', '320x480>', '-strip', '-quality', '82', outputPath);
  await runMagick(argumentsList);
  return outputName;
}

async function main() {
  await mkdir(outputDirectory, { recursive: true });
  const sourceNames = (await readdir(sourceDirectory))
    .filter((name) => supportedExtensions.has(path.extname(name).toLowerCase()))
    .sort((left, right) => left.localeCompare(right));

  if (!sourceNames.length) throw new Error(`No cover images found in ${sourceDirectory}`);
  for (const sourceName of sourceNames) {
    const outputName = await generateThumbnail(sourceName);
    process.stdout.write(`${sourceName} → ${outputName}\n`);
  }
}

main().catch((error) => {
  process.stderr.write(`Unable to generate book thumbnails: ${error.message}\n`);
  process.exitCode = 1;
});
