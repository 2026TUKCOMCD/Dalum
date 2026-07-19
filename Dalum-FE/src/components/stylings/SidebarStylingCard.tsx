import type { MainStylingItem } from '../../types/stylings/Styling.types';

type Props = {
  item: MainStylingItem;
};

const SidebarStylingCard = ({ item }: Props) => {
  return (
    <>
      {/* 제품 사진 */}
      <div className="w-60 h-60 justify-center items-center flex">
        <img
          alt="업로드 이미지"
          src={item.imageUrl}
          className="w-60 h-60 rounded-sm bg-center border border-primary-600 object-contain"
        />
      </div>
    </>
  );
};

export default SidebarStylingCard;
