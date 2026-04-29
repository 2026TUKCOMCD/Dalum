import { useNavigate } from 'react-router-dom';
import type { DupeSearchItem, StylingItem } from '../../types/me/Me.types';
import { formatDate, isDupeSearchItem } from '../../utils';
import { useMeStore } from '../../stores/me/meStore';
import TrashIcon from '../../assets/icons/TrashIcon';
import useBaseModal from '../../stores/modals/baseModal';
import type React from 'react';

type Props = {
  item: DupeSearchItem | StylingItem;
};

const HistoryCard = ({ item }: Props) => {
  const navigate = useNavigate();
  const { openModal } = useBaseModal();
  const { setDeleteTarget } = useMeStore();

  const imageUrl = isDupeSearchItem(item)
    ? `${item.inputImageUrl}`
    : `${item.imageUrl}`;

  const time = isDupeSearchItem(item)
    ? `${item.searchTime}`
    : `${item.createdAt}`;

  const dateText = isDupeSearchItem(item) ? `검색일시` : `저장일시`;

  const handleClickCard = () => {
    if (isDupeSearchItem(item)) {
      navigate(`/result/${item.searchLogId}`);
    } else {
      navigate(`/styling/${item.stylingId}`);
    }
  };

  const handleClickDelete = (e: React.MouseEvent) => {
    e.stopPropagation();

    setDeleteTarget(item);
    openModal('historyDeleteModal');
  };

  return (
    <div
      className="w-45 h-fit flex flex-col gap-2 cursor-pointer"
      onClick={handleClickCard}
    >
      <div className="h-45 flex items-center justify-center rounded-sm">
        <img
          src={imageUrl}
          className="h-full object-contain rounded-sm shadow-image-shadow"
        />
      </div>
      <div className="flex flex-col gap-1 px-1 py-0.5 text-gray-900">
        <div className="w-full h-fit flex items-center justify-between">
          <span className="typo-body_bold12">| {dateText}</span>
          <button
            type="button"
            onClick={handleClickDelete}
            className="cursor-pointer"
          >
            <TrashIcon className="size-3 text-gray-300" />
          </button>
        </div>
        <span className="typo-body_med12">{formatDate(new Date(time))}</span>
      </div>
    </div>
  );
};

export default HistoryCard;
