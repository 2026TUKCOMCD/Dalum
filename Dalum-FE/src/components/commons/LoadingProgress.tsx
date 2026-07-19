const LoadingProgress = ({ text = '로딩 중...' }: { text?: string }) => {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70">
      <div className="flex flex-col items-center gap-5">
        {/* 스피너 */}
        <div className="w-12 h-12 border-4 border-gray-0 border-t-transparent rounded-full animate-spin" />

        {/* 텍스트 */}
        <span className="typo-body_bold20 text-gray-0">{text}</span>
      </div>
    </div>
  );
};

export default LoadingProgress;
