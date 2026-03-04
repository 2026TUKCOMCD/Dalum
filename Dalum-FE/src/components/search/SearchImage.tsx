import type React from 'react';
import { Button } from '../commons/Button';
import UploadIcon from '../../assets/icons/UploadIcon';

type Props = {
  fileInputRef: React.RefObject<HTMLInputElement | null>;
  imageFile: File | null;
  previewUrl: string;

  openFilePicker: () => void;
  onChangeFile: (e: React.ChangeEvent<HTMLInputElement>) => void;
  removeImage: () => void;
};

const SearchImage = ({
  fileInputRef,
  imageFile,
  previewUrl,
  openFilePicker,
  onChangeFile,
  removeImage,
}: Props) => {
  return (
    <div className="w-full items-start justify-start flex flex-col gap-7.5">
      <span className="typo-h2_bold24 text-gray-900">| 제품 이미지</span>
      {/* 이미지 업로드 영역 */}
      <div className="w-full flex gap-12.5">
        {/* 이미지 업로드 */}
        <div className="w-1/2 h-100 p-5 border border-gray-900 rounded-lg flex flex-col items-center justify-center gap-5">
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={onChangeFile}
            className="hidden"
          />
          {!imageFile ? (
            <>
              <Button
                variant="gray"
                size="md"
                leftIcon={<UploadIcon className="size-4" />}
                onClick={openFilePicker}
              >
                파일 선택
              </Button>
              <span className="typo-body_med18 text-gray-800 opacity-50">
                이미지를 업로드하고 듀프 제품을 찾아보세요
              </span>
            </>
          ) : (
            <div className="w-full max-h-100 flex flex-col items-center justify-center gap-4 p-5">
              {/* 미리보기 */}
              <img
                src={previewUrl}
                alt="업로드 미리보기"
                className="h-full w-auto rounded-lg object-contain border border-gray-500"
              />
            </div>
          )}
        </div>
        {/* 설명 */}
        <div className="w-1/2 flex flex-col gap-5 item-start justify-end">
          <div className="flex flex-col gap-3 typo-body_bold16">
            <span>| 유의 사항</span>

            <div className="typo-body_thin14 flex flex-col justify-center items-start">
              <span>· 제품 이미지는 최대 1장만 업로드 가능합니다.</span>
              <span>
                · 제품 외의 영역이 적을수록 더 높은 유사도를 지닌 제품을 추천
                받을 수 있습니다.
              </span>
              <span>
                · 검색 결과로 제공되는 제품은 매일 00:00을 기준으로 업데이트
                됩니다.
              </span>
            </div>
          </div>
          {imageFile && (
            <div className="w-full flex flex-col gap-2.5">
              <Button
                variant="primary"
                size="md"
                fullWidth
                onClick={openFilePicker}
              >
                다른 이미지 선택
              </Button>
              <Button
                variant="primary"
                size="md"
                fullWidth
                onClick={removeImage}
              >
                이미지 제거
              </Button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SearchImage;
