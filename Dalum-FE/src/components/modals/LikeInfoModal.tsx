const LikeInfoModal = () => {
  return (
    <div className="flex flex-col gap-2.5 p-6 items-center justify-center w-fit h-fit bg-screen-default rounded-[14px]">
      <span className="typo-body_bold20 text-gray-900">
        마음에 드는 제품은 좋아요를 눌러보세요!
      </span>
      <span className="typo-body_thin16 text-gray-900">
        좋아요한 제품은 마이 페이지에서 스타일링 추천을 받아볼 수 있습니다.
      </span>
    </div>
  );
};

export default LikeInfoModal;
