import React, { useMemo, useRef, useState } from 'react';
import { Button } from '../components/commons/Button';
import type {
  PriceRange,
  SearchDupeProductsRequest,
} from '../types/search/Search.types';
import { useSearchStore } from '../stores/search/searchStore';
import { useNavigate } from 'react-router-dom';
import { PRICE_RANGE_MAP } from '../constants';
import SearchImage from '../components/search/SearchImage';
import SearchCondition from '../components/search/SearchCondition';

const SearchPage = () => {
  const { searchDupe, isLoading } = useSearchStore();
  const { searchLogId } = useSearchStore();
  const navigate = useNavigate();

  const [selected, setSelected] = useState('');
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [brandInput, setBrandInput] = useState('');

  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const getPriceRange = (selected: string): PriceRange =>
    PRICE_RANGE_MAP[selected] ?? {};

  // 미리보기 URL
  const previewUrl = useMemo(() => {
    if (!imageFile) return '';
    return URL.createObjectURL(imageFile);
  }, [imageFile]);

  React.useEffect(() => {
    return () => {
      if (previewUrl) URL.revokeObjectURL(previewUrl);
    };
  }, [previewUrl]);

  const openFilePicker = () => {
    fileInputRef.current?.click();
  };

  const onChangeFile = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
      alert('이미지 파일만 업로드할 수 있어요.');
      e.target.value = '';
      return;
    }

    setImageFile(file);

    e.target.value = '';
  };

  const removeImage = () => {
    setImageFile(null);
  };

  const onClickSearch = async () => {
    if (!imageFile) return;

    const priceRange = getPriceRange(selected);

    const payload: SearchDupeProductsRequest = {
      image: imageFile,
      ...(brandInput.trim() && { brand: brandInput.trim() }),
      ...priceRange,
    };

    try {
      await searchDupe(payload);
      navigate(`/result/${searchLogId}`);
    } catch {
      alert('듀프 제품 검색 실패');
    }
  };

  return (
    <div className="w-full min-h-dvh flex flex-col px-37.5 py-25 items-center justify-center gap-12.5">
      <div className="w-full h-full flex flex-col gap-12.5 items-start">
        {/* 이미지 업로드 영역 */}
        <SearchImage
          fileInputRef={fileInputRef}
          imageFile={imageFile}
          previewUrl={previewUrl}
          openFilePicker={openFilePicker}
          onChangeFile={onChangeFile}
          removeImage={removeImage}
        />

        {/* 조건 설정 영역 */}
        <SearchCondition
          brandInput={brandInput}
          setBrandInput={setBrandInput}
          selected={selected}
          setSelected={setSelected}
        />

        {/* CTA */}
        <Button
          variant="cta_primary"
          size="cta"
          fullWidth
          disabled={!selected || !imageFile || isLoading}
          onClick={onClickSearch}
        >
          듀프 제품 찾기
        </Button>
      </div>
    </div>
  );
};

export default SearchPage;
