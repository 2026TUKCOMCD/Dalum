export type LikedItem = {
  id: string;
  brand: string;
  name: string;
  discountRate: number;
  price: number;
  imageUrl: string;
  productUrl: string;
};

export type GetDupeSearchListResponse = {
  code: string;
  isSuccess: boolean;
  message: string;
  result: DupeSearchList;
};

export type DupeSearchList = {
  totalPage: number;
  totalElements: number;
  searchLogs: DupeSearchItem[];
};

export type DupeSearchItem = {
  searchLogId: number;
  inputImageUrl: string;
  searchTime: string;
};

export type GetStylingListResponse = {
  code: string;
  isSuccess: boolean;
  message: string;
  result: StylingList;
};

export type StylingList = {
  stylings: StylingItem[];
};

export type StylingItem = {
  stylingId: number;
  mainProductImageUrl: string;
  createdAt: string;
};
