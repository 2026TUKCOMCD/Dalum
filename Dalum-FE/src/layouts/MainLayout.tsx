import { Outlet } from 'react-router-dom';
import Header from '../components/commons/Header';
// import { useAuthStore } from "../stores/auth/authStore";
// import { useEffect } from "react";

const MainLayout = () => {
  // 임시 토큰 발급 로직 -> 소셜 로그인 연동 이후 제거 예정
  // const { accessToken, refreshToken, createToken } = useAuthStore();

  // useEffect(() => {
  //   (async () => {
  //     try {
  //       await createToken();
  //     } catch {
  //       alert("마스터 토큰 생성 실패");
  //     }
  //   })();
  // }, [createToken]);

  // useEffect(() => {
  //   if (!accessToken || !refreshToken) return;

  //   localStorage.setItem("accessToken", accessToken);
  //   localStorage.setItem("refreshToken", refreshToken);
  // }, [accessToken, refreshToken]);

  return (
    <div className="flex h-dvh flex-col">
      <Header />

      <div className="flex h-0 w-full min-w-5xl flex-1 justify-center items-center overflow-hidden">
        {/* 메인 콘텐츠 영역 + 사이드 패널 */}
        <main className="scrollbar-hide h-full flex-1 overflow-y-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default MainLayout;
