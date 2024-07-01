import { DynamicContextProvider, } from '@dynamic-labs/sdk-react-core';
import { EthereumWalletConnectors } from '@dynamic-labs/ethereum';
import React, { ReactNode } from 'react';

const DynamicProvider:React.FC<{children:ReactNode}> = ({ children }) => {
  return (
    <DynamicContextProvider
      settings={{
        environmentId: '04f8f9e0-87d7-4b9d-9d37-73f19890c1d2',
        walletConnectors: [EthereumWalletConnectors],
      }}
    >
    
        {children}
    
    </DynamicContextProvider>
  );
};

export default DynamicProvider;