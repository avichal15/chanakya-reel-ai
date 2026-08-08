import { GoogleGenAI, Modality, Type } from "@google/genai";
import { RedditPost, ScriptData, Metadata, CaptionSegment } from "../types";
import { getRedditPost, getSubredditTopPosts } from "./reddit";

// Helper to init AI
const getAI = (apiKey: string) => new GoogleGenAI({ apiKey });

// 1. Fetch/Analyze Reddit Post
// Now prioritizes the Real Reddit API for URLs, falls back to Gemini for raw text.
export const analyzePost = async (apiKey: string, input: string): Promise<RedditPost> => {
  const isUrl = input.includes('reddit.com') || input.startsWith('http');
  
  if (isUrl && input.includes('reddit.com')) {
    try {
      console.log("Detected Reddit URL, attempting to fetch via Reddit API...");
      const post = await getRedditPost(input);
      return post;
    } catch (e) {
      console.warn("Reddit API failed, falling back to Gemini extraction:", e);
      // Fallthrough to Gemini logic below
    }
  }

  // Fallback: Use Gemini to parse text or scrape URL via Search Grounding
  const ai = getAI(apiKey);
  let prompt = "";
  let config: any = {};

  if (isUrl) {
    prompt = `Visit this URL and extract the post details: ${input}.
    
    Return the result as a raw JSON object (no markdown, no code blocks) with the following structure:
    {
      "title": "Post Title",
      "content": "Post Content body text",
      "subreddit": "r/SubredditName",
      "author": "u/Username",
      "url": "${input}"
    }`;
    
    config = {
      tools: [{ googleSearch: {} }]
    };
  } else {
    prompt = `Analyze this text as a Reddit post: "${input}". Return JSON.`;
    config = {
      responseMimeType: "application/json",
      responseSchema: {
        type: Type.OBJECT,
        properties: {
          title: { type: Type.STRING },
          content: { type: Type.STRING },
          subreddit: { type: Type.STRING },
          author: { type: Type.STRING },
          url: { type: Type.STRING },
        },
        required: ['title', 'content', 'subreddit'],
      }
    };
  }

  const response = await ai.models.generateContent({
    model: 'gemini-2.5-flash',
    contents: prompt,
    config: config
  });

  let text = response.text || "{}";
  
  if (text.includes("```")) {
     text = text.replace(/```json/g, "").replace(/```/g, "").trim();
  }

  try {
    const raw = JSON.parse(text);
    return {
      title: raw.title || "Untitled Post",
      content: raw.content || "",
      subreddit: raw.subreddit || "r/reddit",
      author: raw.author || "u/unknown",
      url: raw.url || (isUrl ? input : "")
    } as RedditPost;
  } catch (e) {
    console.error("Failed to parse Reddit post JSON:", text);
    throw new Error("Failed to parse Reddit post. The AI response was not valid JSON.");
  }
};

// 1.5 Fetch Top Posts (Discovery)
// Uses Reddit API directly for better accuracy
export const getTopPosts = async (apiKey: string, subreddit: string): Promise<RedditPost[]> => {
  try {
    return await getSubredditTopPosts(subreddit);
  } catch (e) {
    console.warn("Reddit API Discovery failed, falling back to Gemini Search:", e);
    // Fallback to Gemini Search Grounding
    const ai = getAI(apiKey);
    const prompt = `Find the top 3 trending text-based posts on ${subreddit} from today or this week. 
    Extract the title, content preview (or full content if short), author, and url for each.
    Return a raw JSON array of objects with keys: title, content, subreddit, author, url.`;

    const response = await ai.models.generateContent({
      model: 'gemini-2.5-flash',
      contents: prompt,
      config: {
        tools: [{ googleSearch: {} }]
      }
    });

    let text = response.text || "[]";
    if (text.includes("```")) {
      text = text.replace(/```json/g, "").replace(/```/g, "").trim();
    }

    try {
      const parsed = JSON.parse(text);
      if (Array.isArray(parsed)) return parsed;
      if (parsed.posts && Array.isArray(parsed.posts)) return parsed.posts;
      return [];
    } catch (parseError) {
      console.warn("Failed to parse top posts from Gemini:", text);
      return [];
    }
  }
};

// 1.6 Transcribe Audio
export const transcribeAudio = async (apiKey: string, audioBlob: Blob): Promise<string> => {
  const ai = getAI(apiKey);
  
  // Convert Blob to Base64
  const reader = new FileReader();
  const base64Promise = new Promise<string>((resolve) => {
    reader.onloadend = () => {
        const base64 = (reader.result as string).split(',')[1];
        resolve(base64);
    };
    reader.readAsDataURL(audioBlob);
  });
  const base64Audio = await base64Promise;

  const response = await ai.models.generateContent({
    model: 'gemini-2.5-flash',
    contents: {
      parts: [
        { inlineData: { mimeType: audioBlob.type, data: base64Audio } },
        { text: "Transcribe this audio exactly." }
      ]
    }
  });

  return response.text || "";
};

// 2. Generate Script (Updated to use Thinking Mode)
export const generateScript = async (apiKey: string, post: RedditPost): Promise<ScriptData> => {
  const ai = getAI(apiKey);
  
  const prompt = `
    You are a viral content script writer for TikTok and YouTube Shorts.
    Take the following Reddit post and convert it into an engaging, narrated script.
    
    Post Title: ${post.title}
    Post Content: ${post.content}
    Subreddit: ${post.subreddit}

    Requirements:
    1. "fullScript": 30-45 seconds read time. Start with a hook. Simple, conversational language.
    2. "shortScript": 15-20 seconds summary version.
    3. "hook": The first 3 seconds of the script designed to stop scrolling.
    4. "captions": Break the "fullScript" into small chunks for subtitles. Each chunk should be 3-6 words max.
       Estimate "start" and "end" times (in seconds) assuming a normal speaking pace (approx 150 words per minute).
       The start of the first segment is 0.

    Return JSON.
  `;

  // gemini-2.5-flash: gemma models 500 on this key and don't support responseSchema
  const response = await ai.models.generateContent({
    model: 'gemini-2.5-flash',
    contents: prompt,
    config: {
      responseMimeType: "application/json",
      responseSchema: {
        type: Type.OBJECT,
        properties: {
          fullScript: { type: Type.STRING },
          shortScript: { type: Type.STRING },
          hook: { type: Type.STRING },
          captions: {
            type: Type.ARRAY,
            items: {
              type: Type.OBJECT,
              properties: {
                text: { type: Type.STRING },
                start: { type: Type.NUMBER },
                end: { type: Type.NUMBER },
              }
            }
          }
        }
      }
    }
  });

  return JSON.parse(response.text || "{}") as ScriptData;
};

// 3. Generate Audio (TTS)
// Gemini TTS returns headerless PCM (s16le); browsers can't play that,
// so we wrap it in a WAV container before handing it to <audio>.
const pcmToWavBlob = (pcm: Uint8Array, sampleRate: number, numChannels = 1, bitsPerSample = 16): Blob => {
  const header = new ArrayBuffer(44);
  const view = new DataView(header);
  const byteRate = (sampleRate * numChannels * bitsPerSample) / 8;
  const blockAlign = (numChannels * bitsPerSample) / 8;
  const writeStr = (offset: number, s: string) => {
    for (let i = 0; i < s.length; i++) view.setUint8(offset + i, s.charCodeAt(i));
  };

  writeStr(0, 'RIFF');
  view.setUint32(4, 36 + pcm.length, true);
  writeStr(8, 'WAVE');
  writeStr(12, 'fmt ');
  view.setUint32(16, 16, true);          // fmt chunk size
  view.setUint16(20, 1, true);           // PCM format
  view.setUint16(22, numChannels, true);
  view.setUint32(24, sampleRate, true);
  view.setUint32(28, byteRate, true);
  view.setUint16(32, blockAlign, true);
  view.setUint16(34, bitsPerSample, true);
  writeStr(36, 'data');
  view.setUint32(40, pcm.length, true);

  return new Blob([header, pcm], { type: 'audio/wav' });
};

export const generateSpeech = async (apiKey: string, text: string, voiceName: string): Promise<Blob> => {
  const ai = getAI(apiKey);

  const response = await ai.models.generateContent({
    model: 'gemini-2.5-flash-preview-tts',
    contents: [{ parts: [{ text }] }],
    config: {
      responseModalities: [Modality.AUDIO],
      speechConfig: {
        voiceConfig: {
          prebuiltVoiceConfig: { voiceName }
        }
      }
    }
  });

  const inlineData = response.candidates?.[0]?.content?.parts?.[0]?.inlineData;
  if (!inlineData?.data) throw new Error("No audio generated");

  const binaryString = atob(inlineData.data);
  const len = binaryString.length;
  const bytes = new Uint8Array(len);
  for (let i = 0; i < len; i++) {
    bytes[i] = binaryString.charCodeAt(i);
  }

  // mimeType looks like "audio/L16;codec=pcm;rate=24000"
  const rateMatch = inlineData.mimeType?.match(/rate=(\d+)/);
  const sampleRate = rateMatch ? parseInt(rateMatch[1], 10) : 24000;

  return pcmToWavBlob(bytes, sampleRate);
};

// 4. Generate Veo Video Background (Supports Text-to-Video and Image-to-Video)
export const generateVeoBackground = async (apiKey: string, description: string, imageBase64?: string): Promise<string> => {
  const ai = getAI(apiKey);
  
  const prompt = `A vertical 9:16 high quality background video suitable for a viral short. 
  Theme: ${description}. 
  Style: Cinematic, smooth motion, abstract or realistic, looping texture if possible. No text.`;

  let operation;
  
  try {
    if (imageBase64) {
      // Image-to-Video
      operation = await ai.models.generateVideos({
        model: 'veo-3.1-fast-generate-preview',
        prompt: prompt, // Prompt is optional for I2V but helpful for context
        image: {
            imageBytes: imageBase64,
            mimeType: 'image/png' // Assuming png/jpeg, Veo handles standard types
        },
        config: {
          numberOfVideos: 1,
          resolution: '720p',
          aspectRatio: '9:16'
        }
      });
    } else {
      // Text-to-Video
      operation = await ai.models.generateVideos({
        model: 'veo-3.1-fast-generate-preview',
        prompt,
        config: {
          numberOfVideos: 1,
          resolution: '720p',
          aspectRatio: '9:16'
        }
      });
    }
  } catch (e: any) {
    console.error("Veo Generation Start Error:", e);
    throw new Error(`Failed to start Veo generation: ${e.message || "Unknown error"}`);
  }

  try {
    // Polling with safety timeout and retry logic could be enhanced here
    // For now, simpler polling loop
    let attempts = 0;
    while (!operation.done && attempts < 60) { // Timeout after ~10 minutes
      await new Promise(resolve => setTimeout(resolve, 10000));
      operation = await ai.operations.getVideosOperation({ operation });
      if (operation.error) {
        throw new Error(`Veo operation failed: ${operation.error.message || "Unknown error"}`);
      }
      attempts++;
    }
    if (!operation.done) throw new Error("Video generation timed out.");
  } catch (e: any) {
    console.error("Veo Polling Error:", e);
    throw new Error(`Veo generation failed during polling: ${e.message}`);
  }

  const videoUri = operation.response?.generatedVideos?.[0]?.video?.uri;
  if (!videoUri) throw new Error("Veo completed but returned no video URI.");
  
  // Wait a moment for file propagation
  await new Promise(resolve => setTimeout(resolve, 2000));

  // Fix: Handle cases where videoUri might already have query params
  const separator = videoUri.includes('?') ? '&' : '?';
  const fetchUrl = `${videoUri}${separator}key=${apiKey}`;
  
  let videoResponse;
  try {
      videoResponse = await fetch(fetchUrl);
  } catch (e) {
      throw new Error("Network error while fetching generated video.");
  }
  
  if (!videoResponse.ok) {
    const errorText = await videoResponse.text();
    console.error("Veo Fetch Error Body:", errorText);
    throw new Error(`Failed to download video (Status ${videoResponse.status}). Error: ${errorText || 'Unknown'}`);
  }

  const blob = await videoResponse.blob();
  return URL.createObjectURL(blob);
};

// 4.5 Generate Avatar (Imagen)
export const generateAvatar = async (apiKey: string, prompt: string): Promise<string> => {
  const ai = getAI(apiKey);
  
  const fullPrompt = `A high quality vertical portrait of a character: ${prompt}. 
  Centered composition, facing forward, eyes open. High detail, 8k resolution.
  Solid or simple background.`;

  const response = await ai.models.generateContent({
    model: 'gemini-3-pro-image-preview',
    contents: {
      parts: [
        {
          text: fullPrompt,
        },
      ],
    },
    config: {
      imageConfig: {
          aspectRatio: "9:16",
          imageSize: "1K"
      },
    },
  });

  for (const part of response.candidates?.[0]?.content?.parts || []) {
    if (part.inlineData) {
      const base64EncodeString = part.inlineData.data;
      return base64EncodeString; // Return raw base64 for Veo consumption
    }
  }
  
  throw new Error("No avatar image generated.");
};

// 5. Generate Thumbnail (Imagen)
export const generateThumbnail = async (apiKey: string, scriptSummary: string): Promise<string> => {
  const ai = getAI(apiKey);
  
  const prompt = `A viral, high-contrast, clickbait style 9:16 vertical cover image for a social media video about: ${scriptSummary}. 
  Vibrant colors, shocking or emotional visual, clear focal point, hyper-realistic or illustrative style. No text.`;

  const response = await ai.models.generateContent({
    model: 'gemini-3-pro-image-preview',
    contents: {
      parts: [
        {
          text: prompt,
        },
      ],
    },
    config: {
      imageConfig: {
          aspectRatio: "9:16",
          imageSize: "1K"
      },
    },
  });

  for (const part of response.candidates?.[0]?.content?.parts || []) {
    if (part.inlineData) {
      const base64EncodeString = part.inlineData.data;
      return `data:image/png;base64,${base64EncodeString}`;
    }
  }
  
  throw new Error("No image generated in response.");
};


// 6. Generate Metadata
export const generateMetadata = async (apiKey: string, post: RedditPost, script: string): Promise<Metadata> => {
  const ai = getAI(apiKey);

  const prompt = `
    Generate viral social media metadata for this video script derived from a Reddit post.
    
    Subreddit: ${post.subreddit}
    Script: ${script}
    
    Requirements:
    - YouTube Title: Clickbait but honest, emotional, under 70 chars.
    - YouTube Desc: Short summary + hook.
    - Instagram Caption: Engaging question + call to action.
    - Tags/Hashtags: Mix of broad and niche tags.
    
    Return JSON.
  `;

  const response = await ai.models.generateContent({
    model: 'gemini-2.5-flash',
    contents: prompt,
    config: {
      responseMimeType: "application/json",
      responseSchema: {
        type: Type.OBJECT,
        properties: {
          youtubeTitle: { type: Type.STRING },
          youtubeDescription: { type: Type.STRING },
          youtubeTags: { type: Type.ARRAY, items: { type: Type.STRING } },
          instagramCaption: { type: Type.STRING },
          instagramHashtags: { type: Type.ARRAY, items: { type: Type.STRING } }
        }
      }
    }
  });

  return JSON.parse(response.text || "{}") as Metadata;
};