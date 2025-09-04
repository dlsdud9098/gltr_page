import axios from 'axios';
import { Webtoon, WebtoonEdit, PaginatedWebtoons } from '../types/webtoon';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const webtoonApi = {
  getAllWebtoons: async (page: number = 1, perPage: number = 20): Promise<PaginatedWebtoons> => {
    const response = await axios.get(`${API_BASE_URL}/api/webtoons`, {
      params: {
        page,
        per_page: perPage
      }
    });
    return response.data;
  },

  getWebtoonById: async (id: number): Promise<Webtoon> => {
    const response = await axios.get(`${API_BASE_URL}/api/webtoons/${id}`);
    return response.data;
  },

  editWebtoon: async (id: number, edit: WebtoonEdit) => {
    const response = await axios.post(`${API_BASE_URL}/api/webtoons/${id}/edit`, edit);
    return response.data;
  }
};