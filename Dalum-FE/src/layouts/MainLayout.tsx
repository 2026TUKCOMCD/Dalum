import { Outlet } from "react-router-dom";
import Header from "../components/commons/Header";

const MainLayout = () => {
  return (
    <div className="flex h-dvh flex-col">
      <Header />

      <div className="flex h-0 w-full min-w-5xl flex-1 justify-center overflow-hidden">
        {/* 메인 콘텐츠 영역 + 사이드 패널 */}
        <main className="scrollbar-hide h-full flex-1 overflow-y-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default MainLayout;
