export interface RedditPost {
  title: string;
  content: string;
  subreddit: string;
  author: string;
  url: string;
}

export interface ScriptData {
  fullScript: string;
  shortScript: string;
  hook: string;
  captions: CaptionSegment[];
}

export interface CaptionSegment {
  text: string;
  start: number;
  end: number;
}

export interface Metadata {
  youtubeTitle: string;
  youtubeDescription: string;
  youtubeTags: string[];
  instagramCaption: string;
  instagramHashtags: string[];
}

export interface CaptionStyle {
  fontFamily: string;
  fontSize: number;
  textColor: string;
  outlineColor: string;
  outlineWidth: number;
  shadowColor: string;
  shadowBlur: number;
  isUppercase: boolean;
  yOffset: number; // Position from bottom %
}

export interface MusicTrack {
  name: string;
  url: string;
  category: 'Happy' | 'Dark' | 'Chill' | 'Action';
}

export interface AppState {
  apiKey: string | null;
  post: RedditPost | null;
  script: ScriptData | null;
  audioBlob: Blob | null;
  audioUrl: string | null;
  backgroundVideoUrl: string | null;
  thumbnailUrl: string | null;
  metadata: Metadata | null;
  captionStyle: CaptionStyle;
  
  // Avatar State
  avatarImageUrl: string | null;
  
  // Audio State
  musicUrl: string | null;
  musicVolume: number; // 0.0 to 1.0

  isProcessing: boolean;
  statusMessage: string;
}

export enum Step {
  INPUT = 0,
  SCRIPT = 1,
  VOICE_VIDEO = 2,
  METADATA = 3,
}

export const VOICES = [
  { name: 'Kore (Female - Soft)', id: 'Kore' },
  { name: 'Puck (Neutral)', id: 'Puck' },
  { name: 'Fenrir (Male - Deep)', id: 'Fenrir' },
  { name: 'Zephyr (Male - Calm)', id: 'Zephyr' },
];