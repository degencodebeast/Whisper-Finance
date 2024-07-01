import { apiPost } from "@/utils";
import { useDynamicContext,useUserWallets } from "@dynamic-labs/sdk-react-core";

import { useCallback, useEffect, useState } from "react";

export const useUserBalance = () => {
 
  const { primaryWallet } = useDynamicContext();

  const [balance, setBalance] = useState<string>();
  
  useEffect(() => {
    const fetchBalance = async () => {
      if (primaryWallet) {
        const value = await primaryWallet.connector.getBalance();
        setBalance(value);
      }
    };
    fetchBalance();
  }, [primaryWallet]);
  console.log({balance});
  
  return { balance: balance||'0'};
};
export const useWalletAccount = () => {
  const [_address, setAddress] = useState<string | null>(null);
const wallets=useUserWallets()
const wallet=wallets?.[0]
 const address=wallet?.address
  useEffect(() => {
    if (address) {
      setAddress(address);
    } else {
      setAddress(null);
    }
  }, [address]);

  return { address: _address };
};