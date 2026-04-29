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
  imageUrl?: string;
  createdAt: string;
};

export type GetLikeListResponse = {
  code: string;
  isSuccess: boolean;
  message: string;
  result: LikeList;
};

export type LikeList = {
  totalPage: number;
  totalElements: number;
  likeProducts: LikeItem[];
};

export type LikeItem = {
  productId: number;
  brand: string;
  name: string;
  discount_rate: number;
  discount_price: number;
  imageUrl: string;
  purchase_link: string;
  isLiked: boolean;
};

export type GetDetailDupeSearchResponse = {
  code: string;
  isSuccess: boolean;
  message: string;
  result: DetailDupeSearchList;
};

export type DetailDupeSearchList = {
  searchLogId: number;
  searchDate: string;
  imageUrl: string;
  conditions: {
    minPrice: number | null;
    maxPrice: number | null;
  };
  results: DetailDupeSearchItem[];
};

export type DetailDupeSearchItem = {
  brand: string;
  category: string;
  discountRate: number;
  imageUrl: string;
  isLiked: boolean;
  name: string;
  price: number;
  productId: number;
  purchaseUrl: string | null;
  similarity: string | null;
};

export type DeleteHistoryResponse = {
  code: string;
  isSuccess: boolean;
  message: string;
  result: null;
};
