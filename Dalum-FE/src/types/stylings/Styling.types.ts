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
  resultItems: [];
  createdAt: string;
};

export type MainStylingItem = {
  productId: number;
  name: string;
  brand: string;
  category: string;
  price: number;
  imageUrl: string;
  purchaseUrl: string;
  similarity: string;
  isLiked: boolean;
};

// export type StylingItemList = {
//   category: string;
//         categoryName: string;
//         items: [
//           { "productId": 102, "name": "와이드 팬츠", "price": 39000, "isLiked": false, ... },
//           { "productId": 103, "name": "카고 팬츠", "price": 42000, "isLiked": true, ... }
//         ]
// }

// export type StylingItem = {

// }
