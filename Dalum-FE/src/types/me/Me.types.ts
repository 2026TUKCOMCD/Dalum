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
