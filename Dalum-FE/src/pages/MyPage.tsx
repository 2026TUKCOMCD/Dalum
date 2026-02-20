import ChevronRightIcon from "../assets/icons/ChevronRightIcon";
import UserIfno from "../components/users/UserInfo";
import UserLikedProduct from "../components/users/UserLikedProduct";
import UserResearchHistory from "../components/users/UserResearchHistory";
import UserSavedStyling from "../components/users/UserSavedStyling";
import useBaseModal from "../stores/modals/baseModal";

const MyPage = () => {
  const { openModal } = useBaseModal();

  return (
    <div className="w-full min-h-dvh flex flex-col px-25 py-12.5 items-center justify-center gap-15 overflow-y-auto scrollbar-hide">
      <div className="w-full h-full flex flex-col gap-10 items-start">
        {/* 제목 */}
        <span className="typo-h2_bold24 text-gray-900">| 마이 페이지</span>

        {/* 사용자 정보 영역 */}
        <UserIfno />

        {/* '내가 찾은 듀프 제품' 영역 */}
        <UserResearchHistory />

        {/* '좋아요한 제품' 영역 */}
        <UserLikedProduct />

        {/* '저장한 스타일링' 영역 */}
        <UserSavedStyling />
      </div>

      <div className="w-full flex flex-col justify-center items-start gap-2.5">
        <div
          className="w-full flex items-center justify-start p-4 rounded-lg bg-none text-gray-900 hover:text-primary-900 hover:bg-secondary-900 cursor-pointer gap-1"
          onClick={() => {
            openModal("logoutModal");
          }}
        >
          <span className="typo-body_med16">로그아웃</span>
          <ChevronRightIcon className="size-3" />
        </div>
        <div
          className="w-full flex items-center justify-start p-4 rounded-lg bg-none text-gray-900 hover:text-button-like hover:bg-button-like/10 cursor-pointer gap-1"
          onClick={() => {
            openModal("withdrawModal");
          }}
        >
          <span className="typo-body_med16">회원 탈퇴</span>
          <ChevronRightIcon className="size-3" />
        </div>
      </div>
    </div>
  );
};

export default MyPage;
