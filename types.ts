export enum Tone {
  MOTIVATIONAL = 'Motivational',
  AGGRESSIVE = 'Aggressive',
  STOIC = 'Stoic',
  CONTROVERSIAL = 'Controversial',
  LUXURY = 'Luxury'
}

export interface Quote {
  id: string;
  text: string;
  source: string;
  translation?: string;
  meaning?: string;
  tags: string[];
}

export interface ScriptSection {
  type: 'hook' | 'authority' | 'explanation' | 'example' | 'provocation' | 'cta';
  content: string;
  durationEstimate: number; // in seconds
}

export interface GeneratedScript {
  id: string;
  sections: ScriptSection[];
  fullText: string;
  visualPrompts: string[];
  estimatedDuration: number;
  rage_bait_title?: string;
}

export interface ReelProject {
  id: string;
  quote: Quote;
  script: GeneratedScript | null;
  status: 'draft' | 'scripting' | 'production' | 'completed';
  settings: {
    rageLevel: number; // 1-10
    tone: Tone;
    bgMusic: string;
    voiceId: string;
  };
  createdAt: Date;
}

// Mock themes removed

export const MOCK_VOICES = [
  { id: 'XOWNrvKZm7D6lCsdDP32', name: 'Sigma Male Narrator', gender: 'Male' },
  { id: 'Gfau5REQnRmPRmvm2yHl', name: 'Deep Stoic Voice', gender: 'Male' },
  { id: 'oYoZ8lTszuJOoALnxj1k', name: 'Calm Philosophy Narrator', gender: 'Male' },
  { id: '1hKoYIXeSp6CmcsOoEco', name: 'Dark Cinematic Voice', gender: 'Male' },
];

export interface ExportHistoryRecord {
  id: number;
  video_path: string;
  video_url: string;
  caption_text: string;
  status: string;
  created_at: string;
}