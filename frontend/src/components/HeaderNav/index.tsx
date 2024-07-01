import { Button, HStack, Heading } from "@chakra-ui/react";
import WalletConnectButton from "@/components/WalletConnectButton";
import Link from "next/link";

export default function HeaderNav() {
  return (
    <HStack
      borderBottom={"1px"}
      borderBottomColor={"gray.600"}
      py={{ lg: 4, base: 3 }}
      minH={10}
      justify={"space-between"}
      px={{ lg: 4, base: 3 }}
    >
      <Heading>
        <Link href={"/"}>Whisper Finance</Link>
      </Heading>
      <nav></nav>

      <WalletConnectButton />
    </HStack>
  );
}
