// 유저 정보 조회 API 응답 타입
export type GetUserInfoResponse = {
  code: string;
  isSuccess: boolean;
  message: string;
  result: UserItem;
};

// 유저 정보 아이템
export type UserItem = {
  memberId: number;
  nickname: string;
  loginType: string;
};
