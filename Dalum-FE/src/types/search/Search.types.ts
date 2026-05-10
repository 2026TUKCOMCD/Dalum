export type PriceRange = {
  minPrice?: number;
  maxPrice?: number;
};

export type SearchDupeProductsRequest = {
  image: File;
  brand?: string;
  minPrice?: number;
  maxPrice?: number;
};

export type SearchDupeProductsResponse = {
  code: string;
  isSuccess: boolean;
  message: string;
  result: SearchDupeProductsData;
};

export type SearchDupeProductsData = {
  searchLogId: number;
  resultCount: number;
  products: DupeProductsItem[];
};

export type DupeProductsItem = {
  productId: number;
  name: string;
  brand: string;
  category: string;
  discountRate: number;
  price: number;
  imageUrl: string;
  purchaseUrl: string;
  isLiked: boolean;
  colorScore: number;
  materialScore: number;
  designScore: number;
  totalScore: number;
};
