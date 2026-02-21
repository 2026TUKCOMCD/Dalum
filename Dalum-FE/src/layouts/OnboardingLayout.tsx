import { Outlet } from 'react-router-dom';

const OnboardingLayout = () => {
  return (
    <div className="flex h-dvh flex-col select-none">
      <div className="flex h-0 w-full min-w-5xl flex-1 justify-center overflow-hidden">
        <main className="h-full flex-1">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default OnboardingLayout;
