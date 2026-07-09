import axios from 'axios';

const api = axios.create({
  baseURL: '/api', // Proxy handles the rest
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getQuotes = async () => {
  const response = await api.get('/quotes/');
  return response.data;
};

export const createQuote = async (quoteData: any) => {
  const response = await api.post('/quotes/', quoteData);
  return response.data;
};

export const createQuotesBulk = async (quotes: any[]) => {
  const response = await api.post('/quotes/bulk', quotes);
  return response.data;
};

export const generateScript = async (quote: string, philosopher: string = "Chanakya", rageLevel: number = 5) => {
  const response = await api.post('/generate-script', {
    quote,
    philosopher,
    rage_level: rageLevel
  });
  return response.data;
};

export const generateVoice = async (text: string, voiceId: string = "JBFqnCBsd6RMkjVDRZzb") => {
  const response = await api.post('/generate-voice', {
    text,
    voice_id: voiceId
  });
  return response.data;
};

export const generateVideo = async (scriptData: any, audioPath: string, backgroundPath?: string, bgVideoPaths?: string[], bgMusicPath?: string, bgMusicVolume?: number, captionSize?: string, useSmartSfx: boolean = true, useAutoBRoll: boolean = false) => {
  const response = await api.post('/generate-video', {
    script_data: scriptData,
    audio_path: audioPath,
    background_path: backgroundPath,
    bg_video_paths: bgVideoPaths,
    bg_music_path: bgMusicPath,
    bg_music_volume: bgMusicVolume,
    caption_size: captionSize,
    use_smart_sfx: useSmartSfx,
    use_auto_b_roll: useAutoBRoll
  });
  return response.data;
};

export const ingestPDF = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post('/ingest/pdf', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    timeout: 300000, // 5 minutes for large PDF chunked extraction
  });
  return response.data;
};

export const generateCaption = async (data: any) => {
  const response = await api.post('/generate-caption', data);
  return response.data;
};

export const uploadBackground = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post('/upload-background', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return response.data;
};

export const uploadAudio = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post('/upload-audio', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return response.data;
};

export const getUploadedVideos = async () => {
  const response = await api.get('/uploads/videos');
  return response.data;
};

export const getUploadedAudio = async () => {
  const response = await api.get('/uploads/audio');
  return response.data;
};

export const deleteUploadedVideo = async (filename: string) => {
  const response = await api.delete(`/uploads/videos/${filename}`);
  return response.data;
};

export const deleteUploadedAudio = async (filename: string) => {
  const response = await api.delete(`/uploads/audio/${filename}`);
  return response.data;
};

export const getExportHistory = async () => {
  const response = await api.get('/history');
  return response.data;
};
