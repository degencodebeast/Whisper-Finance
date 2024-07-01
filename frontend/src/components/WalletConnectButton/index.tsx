import { useWalletAccount } from "@/hooks";
import { maskWalletAddress } from "@/utils";
import { Button, Menu, MenuButton, MenuItem, MenuList } from "@chakra-ui/react";
import { useDynamicContext } from "@dynamic-labs/sdk-react-core";
import { useCallback, useEffect } from "react";
import { BiSolidLogOut } from "react-icons/bi";
import { BsChevronDown } from "react-icons/bs";

export default function WalletConnectButton() {
  const { setShowAuthFlow, } = useDynamicContext();

  const { address } = useWalletAccount();

  async function handleConnect() {
    try {
    setShowAuthFlow(true)
    } catch (error) {}
  }
  async function handleDisconnect() {
    try {
      // await disconnect();
 
    } catch (error) {}
  }
  return (
    <>
      {!address && (
        <Button
          fontWeight={600}
          size={{ md: "lg", base: "md" }}
          onClick={async () => await handleConnect()}
          variant={"outline"}
        >
          Connect Wallet
        </Button>
      )}
      { address && (
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
