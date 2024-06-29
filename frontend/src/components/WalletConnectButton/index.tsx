import { useCustomSign, useWalletAccount } from "@/hooks";
import { maskWalletAddress } from "@/utils";
import { Button, Menu, MenuButton, MenuItem, MenuList } from "@chakra-ui/react";
import { useConnection, useWallet } from "@solana/wallet-adapter-react";
import { useWalletModal } from "@solana/wallet-adapter-react-ui";
import { useCallback, useEffect } from "react";
import { BiSolidLogOut } from "react-icons/bi";
import { BsChevronDown } from "react-icons/bs";

export default function WalletConnectButton() {
  const { connected, disconnect, publicKey, connect } = useWallet();
  const { connection } = useConnection();

  const wm = useWalletModal();
  const { address } = useWalletAccount();
  const { signCustomMessage, signed, setSigned } = useCustomSign();

  async function handleConnect() {
    try {
      wm.setVisible(true);
    } catch (error) {}
  }
  async function handleDisconnect() {
    try {
      await disconnect();
      setSigned(false);
    } catch (error) {}
  }
  // useEffect(() => {
  //   const signMessageCb = async () => {
  //     if (publicKey) {
  //       if (!signed) {
  //         await signCustomMessage();
  //         await new Promise((resolve) => setTimeout(resolve, 2000));
  //       }
  //     } else {
  //       setSigned(false);
  //     }
  //     if (signed) {
  //       connection
  //         .getBalance(publicKey!)
  //         .then((balance) => console.log({ balance }));
  //     }
  //   };
  //   signMessageCb();
  //   // eslint-disable-next-line react-hooks/exhaustive-deps
  // }, [publicKey, signed]);
  return (
    <>
      {!connected && (
        <Button
          fontWeight={600}
          size={{ md: "lg", base: "md" }}
          onClick={async () => await handleConnect()}
          variant={"outline"}
        >
          Connect Wallet
        </Button>
      )}
      {connected && publicKey && (
        <Menu>
          <MenuButton
            rightIcon={<BsChevronDown />}
            as={Button}
            colorScheme="gray"
          >
            {maskWalletAddress(address!)}
          </MenuButton>
          <MenuList>
            <MenuItem
              icon={<BiSolidLogOut />}
              onClick={async () => await handleDisconnect()}
            >
              disconnect
            </MenuItem>
          </MenuList>
        </Menu>
      )}
    </>
  );
}
