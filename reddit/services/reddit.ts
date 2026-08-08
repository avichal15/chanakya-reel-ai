import { RedditPost } from "../types";

// Credentials come from .env (REDDIT_CLIENT_ID / REDDIT_CLIENT_SECRET) via vite define.
const CLIENT_ID = process.env.REDDIT_CLIENT_ID || '';
const CLIENT_SECRET = process.env.REDDIT_CLIENT_SECRET || '';

// --- OAuth token management ---
// Reddit blocks unauthenticated .json scraping (403), so we use the
// client_credentials flow and talk to oauth.reddit.com via the vite proxy.
let cachedToken: { token: string; expiresAt: number } | null = null;

const getAccessToken = async (): Promise<string> => {
  if (cachedToken && Date.now() < cachedToken.expiresAt - 60_000) {
    return cachedToken.token;
  }
  if (!CLIENT_ID || !CLIENT_SECRET) {
    throw new Error("Missing REDDIT_CLIENT_ID / REDDIT_CLIENT_SECRET in .env");
  }

  const response = await fetch('/reddit-oauth/api/v1/access_token', {
    method: 'POST',
    headers: {
      'Authorization': `Basic ${btoa(`${CLIENT_ID}:${CLIENT_SECRET}`)}`,
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: 'grant_type=client_credentials',
  });

  if (!response.ok) {
    throw new Error(`Reddit OAuth failed: ${response.status} ${response.statusText}`);
  }

  const data = await response.json();
  if (!data.access_token) throw new Error("Reddit OAuth returned no access token.");

  cachedToken = {
    token: data.access_token,
    expiresAt: Date.now() + (data.expires_in ?? 3600) * 1000,
  };
  return cachedToken.token;
};

/** Fetch a path (e.g. /r/AskReddit/top?t=day) from oauth.reddit.com via the proxy. */
const fetchRedditJson = async (path: string) => {
  const token = await getAccessToken();
  const separator = path.includes('?') ? '&' : '?';
  const response = await fetch(`/reddit-data${path}${separator}raw_json=1`, {
    headers: { 'Authorization': `Bearer ${token}` },
  });

  if (!response.ok) {
    throw new Error(`Reddit API Error: ${response.status} ${response.statusText}`);
  }
  return response.json();
};

/** Normalize any Reddit URL (www/old/no-subdomain) to its path, e.g. /r/sub/comments/id/title */
const redditUrlToPath = (url: string): string | null => {
  try {
    const u = new URL(url.startsWith('http') ? url : `https://${url}`);
    if (!/(^|\.)reddit\.com$/.test(u.hostname)) return null;
    return u.pathname.replace(/\/$/, '').replace(/\.json$/, '');
  } catch {
    return null;
  }
};

const mapPostData = (p: any): RedditPost => ({
  title: p.title,
  content: p.selftext || (p.url_overridden_by_dest ? `[Media: ${p.url_overridden_by_dest}]` : `(Link Post) ${p.url || ''}`),
  subreddit: `r/${p.subreddit}`,
  author: `u/${p.author}`,
  url: `https://www.reddit.com${p.permalink}`,
});

export const getRedditPost = async (url: string): Promise<RedditPost> => {
  const path = redditUrlToPath(url);
  if (!path) throw new Error(`Not a valid Reddit URL: ${url}`);

  try {
    const data = await fetchRedditJson(path);
    // Post JSON structure: array of 2 listings; the first contains the post.
    const postData = data[0]?.data?.children?.[0]?.data;
    if (!postData) throw new Error('Invalid Reddit post structure received.');
    return mapPostData(postData);
  } catch (e: any) {
    console.error("Reddit Fetch Error:", e);
    throw new Error(`Failed to fetch Reddit post: ${e.message}`);
  }
};

export const getSubredditTopPosts = async (subredditInput: string): Promise<RedditPost[]> => {
  const sub = subredditInput.replace(/^\/?(r\/)?/i, '').replace(/\//g, '').trim();
  if (!sub) throw new Error("Invalid subreddit name");

  try {
    const data = await fetchRedditJson(`/r/${sub}/top?t=day&limit=10`);
    const posts = data.data?.children || [];
    return posts
      .map((child: any) => mapPostData(child.data))
      .filter((p: RedditPost) => !p.title.includes("[Meta]"));
  } catch (e: any) {
    console.error("Reddit Discovery Error:", e);
    throw new Error(`Failed to fetch top posts from r/${sub}: ${e.message}`);
  }
};
