type Provider = 'kakao' | 'naver' | 'google';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

// 카카오/네이버/구글 소셜 로그인 리다이렉트 API
export const redirectToSocialLogin = (provider: Provider) => {
  window.location.href = `${API_BASE_URL}/oauth2/authorization/${provider}`;
};
