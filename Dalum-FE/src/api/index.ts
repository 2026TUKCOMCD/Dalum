import axios, {
  AxiosError,
  AxiosHeaders,
  type AxiosInstance,
  type InternalAxiosRequestConfig,
} from 'axios';
import type { ReissueTokenResponse } from '../types/auth/Auth.types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

declare module 'axios' {
  export interface InternalAxiosRequestConfig {
    skipAuth?: boolean;
    _retry?: boolean;
  }
}

// 쿠키 미포함 API
export const baseApi = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    Accept: 'application/json',
  },
});

// 쿠키 포함 API
export const authApi = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    Accept: 'application/json',
  },
  withCredentials: true,
});

// 요청 헤더 토큰 주입
const addAuthHeader = (config: InternalAxiosRequestConfig) => {
  if (config.skipAuth) return config;

  const token = localStorage.getItem('accessToken');
  if (!token) return config;

  if (config.headers instanceof AxiosHeaders) {
    config.headers.set('Authorization', `Bearer ${token}`);
  } else {
    config.headers = new AxiosHeaders(config.headers);
    config.headers.set('Authorization', `Bearer ${token}`);
  }
  return config;
};

// FormData 형식 사용을 위한 설정
const removeContentTypeIfFormData = (config: InternalAxiosRequestConfig) => {
  if (typeof FormData !== 'undefined' && config.data instanceof FormData) {
    if (config.headers instanceof AxiosHeaders) {
      config.headers.delete('Content-Type');
      config.headers.delete('content-type');
    } else if (config.headers) {
      delete config.headers['Content-Type'];
      delete config.headers['content-type'];
    }
  }
  return config;
};

const requestReissue = async (): Promise<{
  accessToken: string;
  refreshToken?: string;
}> => {
  const refreshToken = localStorage.getItem('refreshToken');
  if (!refreshToken) throw new Error('NO_REFRESH_TOKEN');

  const { data } = await authApi.post<ReissueTokenResponse>(
    '/api/v1/auth/reissue',
    undefined
  );

  const result = data.result;

  if (!result.accessToken) throw new Error('REISSUE_RESPONSE_INVALID');

  return {
    accessToken: result.accessToken,
    refreshToken: result.refreshToken,
  };
};

// 만료 판정
const isAuthExpiredError = (error: AxiosError) => {
  const status = error.response?.status;
  return status === 401; // 보통 만료는 401
};

// refresh 중복 호출 방지 + 대기 큐
let isRefreshing = false;
let refreshQueue: Array<(newToken: string | null) => void> = [];

const flushQueue = (newToken: string | null) => {
  refreshQueue.forEach((cb) => cb(newToken));
  refreshQueue = [];
};

// response interceptor: 401이면 재발급 후 원요청 재시도
const applyResponseInterceptor = (instance: AxiosInstance) => {
  instance.interceptors.response.use(
    (res) => res,
    async (error: AxiosError) => {
      const original = error.config as InternalAxiosRequestConfig | undefined;
      if (!original) return Promise.reject(error);

      // 재발급/로그인 등 skipAuth 요청은 여기서 건드리지 않음
      if (original.skipAuth) return Promise.reject(error);

      // 만료(401) 아니면 그대로 던짐
      if (!isAuthExpiredError(error)) return Promise.reject(error);

      // 무한루프 방지
      if (original._retry) return Promise.reject(error);
      original._retry = true;

      // refreshToken 없으면 끝 (로그아웃 처리)
      const rt = localStorage.getItem('refreshToken');
      if (!rt) {
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        return Promise.reject(error);
      }

      // 이미 재발급 중이면 큐에 넣고 기다렸다가 재시도
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          refreshQueue.push((newToken) => {
            if (!newToken) return reject(error);

            // 새 토큰으로 원요청 헤더 갱신 후 재시도
            if (original.headers instanceof AxiosHeaders) {
              original.headers.set('Authorization', `Bearer ${newToken}`);
            } else {
              original.headers = new AxiosHeaders(original.headers);
              original.headers.set('Authorization', `Bearer ${newToken}`);
            }

            resolve(instance(original));
          });
        });
      }

      // 재발급 시작
      isRefreshing = true;

      try {
        const { accessToken: newAT, refreshToken: newRT } =
          await requestReissue();

        localStorage.setItem('accessToken', newAT);
        if (newRT) localStorage.setItem('refreshToken', newRT);

        // 대기중 요청들 풀어주기
        flushQueue(newAT);

        // 원요청도 새 토큰으로 재시도
        if (original.headers instanceof AxiosHeaders) {
          original.headers.set('Authorization', `Bearer ${newAT}`);
        } else {
          original.headers = new AxiosHeaders(original.headers);
          original.headers.set('Authorization', `Bearer ${newAT}`);
        }

        return instance(original);
      } catch (e) {
        // 재발급 실패 → 토큰 제거
        flushQueue(null);
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');

        window.location.href = '/';

        return Promise.reject(e);
      } finally {
        isRefreshing = false;
      }
    }
  );
};

const applyInterceptors = (instance: AxiosInstance) => {
  instance.interceptors.request.use(addAuthHeader);
  instance.interceptors.request.use(removeContentTypeIfFormData);
  applyResponseInterceptor(instance);
};

applyInterceptors(authApi);
applyInterceptors(baseApi);
