export interface Vault {
  mentions?: {
    [key: string]: string;
  };
  strategy?: string;
  intro?: string;
  risk?: string;

  name: string;
  slug: string;
  cover: string;
  avatar?: string;
  depositTokens?: Array<{ name?: string; image?: string }>;
  tradingTokens?: Array<{ name?: string; image?: string }>;
  apy: string;
  tvl: string;
  capacity: string;
}
