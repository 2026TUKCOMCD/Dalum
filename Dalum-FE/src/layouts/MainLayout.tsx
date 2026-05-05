import { Outlet } from 'react-router-dom';
import Header from '../components/commons/Header';
import { useAuthStore } from '../stores/auth/authStore';
import { useEffect } from 'react';
import LoadingProgress from '../components/commons/LoadingProgress';
import { useStylingStore } from '../stores/stylings/stylingStore';
import { useMemberStore } from '../stores/members/memberStore';
import { useSearchStore } from '../stores/search/searchStore';

const MainLayout = () => {
  // 임시 토큰 발급 로직 -> 소셜 로그인 연동 이후 제거 예정
  const { accessToken, refreshToken, createToken } = useAuthStore();
  const { stylingLoading } = useStylingStore();
  const { isLoading } = useSearchStore();
  const { userData } = useMemberStore();

  useEffect(() => {
    (async () => {
      try {
        await createToken();
      } catch {
        alert('마스터 토큰 생성 실패');
      }
    })();
  }, [createToken]);

  useEffect(() => {
    if (!accessToken || !refreshToken) return;

    localStorage.setItem('accessToken', accessToken);
    localStorage.setItem('refreshToken', refreshToken);
  }, [accessToken, refreshToken]);

  return (
    <div className="flex h-dvh flex-col select-none">
      {stylingLoading && (
        <LoadingProgress
          text={`${userData?.nickname || '사용자'}님에게 어울리는 스타일링을 찾고 있어요!`}
        />
      )}

      {isLoading && (
        <LoadingProgress text="업로드한 이미지를 기반으로 듀프 제품을 찾고 있어요!" />
      )}
      <Header />

      <div className="flex flex-1 min-h-0 w-full min-w-5xl justify-center overflow-hidden">
        {/* 메인 콘텐츠 영역 + 사이드 패널 */}
        <main
          id="page-scroll-container"
          className="flex-1 min-h-0 overflow-y-auto overscroll-contain scrollbar-hide"
        >
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default MainLayout;
