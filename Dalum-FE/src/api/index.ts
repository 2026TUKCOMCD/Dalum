import axios, {
  AxiosHeaders,
  type AxiosInstance,
  type InternalAxiosRequestConfig,
} from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

// 쿠키 미포함 API
export const baseApi = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    Accept: "application/json",
  },
});

// 쿠키 포함 API
export const authApi = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    Accept: "application/json",
  },
  withCredentials: true,
});

// 요청 헤더 토큰 주입
const addAuthHeader = (
  config: InternalAxiosRequestConfig,
): InternalAxiosRequestConfig => {
  const token = localStorage.getItem("accessToken");

  if (token) {
    // headers가 AxiosHeaders인 경우
    if (config.headers instanceof AxiosHeaders) {
      config.headers.set("Authorization", `Bearer ${token}`);
    } else {
      // fallback: 일반 객체일 경우
      config.headers = new AxiosHeaders(config.headers);
      config.headers.set("Authorization", `Bearer ${token}`);
    }
  }

  return config;
};

// FormData 형식 사용을 위한 설정
const removeContentTypeIfFormData = (
  config: InternalAxiosRequestConfig,
): InternalAxiosRequestConfig => {
  if (typeof FormData !== "undefined" && config.data instanceof FormData) {
    if (config.headers instanceof AxiosHeaders) {
      config.headers.delete("Content-Type");
      config.headers.delete("content-type");
    } else if (config.headers) {
      delete config.headers["Content-Type"];
      delete config.headers["content-type"];
    }
  }

  return config;
};

const applyInterceptors = (instance: AxiosInstance) => {
  instance.interceptors.request.use(addAuthHeader);
  instance.interceptors.request.use(removeContentTypeIfFormData);
};

applyInterceptors(authApi);
applyInterceptors(baseApi);
