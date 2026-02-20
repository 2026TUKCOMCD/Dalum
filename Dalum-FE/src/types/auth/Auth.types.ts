export type CreateMasterTokenResponse = {
  isSuccess: boolean;
  code: string;
  message: string;
  result: MasterTokenItem;
};

export type MasterTokenItem = {
  grantType: string;
  accessToken: string;
  refreshToken: string;
  accessTokenExpiresIn: number;
};

export type LogoutAccountResponse = {
  isSuccess: boolean;
  code: string;
  message: string;
  result: string | null;
};
