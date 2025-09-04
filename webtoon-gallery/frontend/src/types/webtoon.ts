export interface Episode {
  episode_number: number;
  title: string;
  images: string[];
  storyboard?: any[];
  published_at?: string | null;
  created_at: string;
}

export interface Webtoon {
  id: number | string;
  title: string;
  description: string;
  thumbnail: string;
  images?: string[];
  author: string;
  episodes?: Episode[] | number;
  total_episodes?: number;
}

export interface WebtoonEdit {
  drawing?: string;
  llm_question?: string;
}

export interface PaginatedWebtoons {
  items: Webtoon[];
  total: number;
  page: number;
  per_page: number;
  has_more: boolean;
}