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
  price: number;
  imageUrl: string;
  purchaseLink: string;
  isLiked: boolean;
  similarity: number;
};
