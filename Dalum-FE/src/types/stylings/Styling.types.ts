export type StylingItem = {
  id: string;
  brand: string;
  name: string;
  discountRate?: number;
  price: number;
  imageUrl: string;
  productUrl: string;
};

export type RecommendStylingResponse = {
  isSuccess: boolean;
  code: string;
  message: string;
  result: RecommendStylingResult;
};

export type RecommendStylingResult = {
  stylingId: number;
  mainItem: MainStylingItem;
  items: ResultStylingItem[];
  createdAt: string;
};

export type SaveStylingResponse = {
  isSuccess: boolean;
  code: string;
  message: string;
  result: SaveStylingResult;
};

export type SaveStylingResult = {
  stylingId: number;
};

export type GetDetailStylingResponse = {
  isSuccess: boolean;
  code: string;
  message: string;
  result: GetDetailStylingResult;
};

export type GetDetailStylingResult = {
  stylingId: number;
  createdAt: string;
  name: string;
  mainProduct: MainStylingItem;
  items: ResultStylingItem[];
};

export type MainStylingItem = {
  productId: number;
  category: string;
  name: string;
  brand: string;
  discountRate?: number;
  discountPrice: number;
  imageUrl: string;
  purchaseUrl: string;
  isLiked: boolean;
};

export type ResultStylingItem = {
  productId: number;
  category: string;
  name: string;
  brand: string;
  discountRate?: number;
  discountPrice: number;
  imageUrl: string;
  purchaseLink: string;
  isLiked: boolean;
};
