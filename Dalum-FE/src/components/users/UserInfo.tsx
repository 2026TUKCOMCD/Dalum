import { useEffect } from 'react';
import { useMemberStore } from '../../stores/members/memberStore';
import { USER_TYPE_MAP } from '../../constants';

const UserIfno = () => {
  const { userData, fetchUser } = useMemberStore();

  // 사용자 정보 조회
  useEffect(() => {
    fetchUser();
  }, [fetchUser]);

  // 로그인 유형 한글 변환
  const userType = userData?.loginType
    ? (USER_TYPE_MAP[userData.loginType] ?? userData.loginType)
    : '-';

  return (
    <div className="w-full flex flex-col gap-4">
      <span className="typo-body_bold16">| 내 정보</span>
      <div className="w-full flex flex-col gap-2.5">
        <div className="w-full flex items-center justify-between p-4 rounded-lg  text-gray-800 hover:bg-secondary-900 transition-colors duration-200 hover:text-primary-900">
          <span className="w-20 typo-body_med14">사용자명</span>
          <span className="typo-body_bold14">{userData?.nickname}</span>
        </div>
        <div className="w-full flex items-center justify-between p-4 rounded-lg typo-body_bold14 text-gray-800 hover:bg-secondary-900 transition-colors duration-200 hover:text-primary-900">
          <span className="w-20 typo-body_med14">로그인 유형</span>
          <span className="typo-body_bold14">{userType}</span>
        </div>
      </div>
    </div>
  );
};

export default UserIfno;
