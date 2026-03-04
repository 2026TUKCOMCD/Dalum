export type ToggleLikeResponse = {
  isSuccess: boolean;
  code: string;
  message: string;
  result: {
    isLiked: boolean;
  };
};
