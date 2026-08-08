import { CaptionStyle, MusicTrack } from './types';

export const DEFAULT_BACKGROUND_VIDEO = "https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerJoyrides.mp4"; // Placeholder

export const SAMPLE_POST = {
  title: "AITA for telling my sister she can't propose at my wedding?",
  content: "My sister (24F) asked if her boyfriend could propose to her during my (27F) wedding reception. I told her absolutely not, as I paid thousands for this day and want it to be about me and my husband. She's now calling me selfish and our parents are taking her side. Am I the asshole?",
  subreddit: "r/AmItheAsshole",
  author: "user123",
  url: "https://reddit.com/r/AmItheAsshole/..."
};

export const PREDEFINED_BACKGROUNDS = [
  { name: "Minecraft Parkour (Demo)", url: "https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerJoyrides.mp4" },
  { name: "Subway Run (Demo)", url: "https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4" },
  { name: "Satisfying Sand (Demo)", url: "https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4" },
  { name: "Abstract Neon (Demo)", url: "https://storage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4" }
];

export const BACKGROUND_MUSIC_TRACKS: MusicTrack[] = [
  { name: "None", url: "", category: 'Chill' },
  { name: "Lo-Fi Chill", url: "https://cdn.pixabay.com/download/audio/2022/05/27/audio_1808fbf07a.mp3?filename=lofi-study-112191.mp3", category: 'Chill' },
  { name: "Suspense/Dark", url: "https://cdn.pixabay.com/download/audio/2022/03/22/audio_c8c8a73467.mp3?filename=background-music-for-videos-dark-ambient-11003.mp3", category: 'Dark' },
  { name: "Upbeat/Happy", url: "https://cdn.pixabay.com/download/audio/2022/01/18/audio_d0a13f69d2.mp3?filename=good-morning-111586.mp3", category: 'Happy' },
  { name: "Action/Fast", url: "https://cdn.pixabay.com/download/audio/2022/04/27/audio_65b3552803.mp3?filename=action-rock-109015.mp3", category: 'Action' }
];

export const DEFAULT_CAPTION_STYLE: CaptionStyle = {
  fontFamily: 'Montserrat',
  fontSize: 24, // Tailwind text-2xl is roughly 24px/1.5rem
  textColor: '#FFFFFF',
  outlineColor: '#000000',
  outlineWidth: 2,
  shadowColor: '#000000',
  shadowBlur: 0,
  isUppercase: true,
  yOffset: 30, // 30% from bottom
};