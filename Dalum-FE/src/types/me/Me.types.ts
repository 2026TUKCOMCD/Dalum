export type HistoryType = "search" | "styling";

export type HistoryItem = {
  id: string;
  type: HistoryType;
  createdAt: string; // "2026.01.15.(목) 05:28" or ISO
  thumbnailUrl?: string; // 있으면 이미지로
};

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
