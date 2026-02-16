const UserIfno = () => {
  return (
    <div className="w-full flex flex-col gap-5">
      <span className="typo-body_bold20">내 정보</span>
      <div className="w-full flex flex-col gap-2.5">
        <div className="w-full flex items-center justify-between p-4 rounded-lg  text-gray-800 hover:bg-secondary-900 transition-colors duration-200 hover:text-primary-900">
          <span className="w-20 typo-body_med16">사용자명</span>
          <span className="typo-body_bold16">진효찬</span>
        </div>
        <div className="w-full flex items-center justify-between p-4 rounded-lg typo-body_bold16 text-gray-800 hover:bg-secondary-900 transition-colors duration-200 hover:text-primary-900">
          <span className="w-20 typo-body_med16">로그인 유형</span>
          <span className="typo-body_bold16">카카오</span>
        </div>
      </div>
    </div>
  );
};

export default UserIfno;
