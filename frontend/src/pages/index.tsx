import HeaderNav from "@/components/HeaderNav";
import VaultCard from "@/components/VaultCard";
import { Box, Flex, Heading, Text } from "@chakra-ui/react";
import { GetServerSidePropsContext, InferGetServerSidePropsType } from "next";
import { vaults } from "@/lib/vaults";

export default function Home({
  vaults,
}: InferGetServerSidePropsType<typeof getServerSideProps>) {
  return (
    <>
      <HeaderNav />
      <main>
        <Box
          mx={"auto"}
          py={8}
          my={6}
          textAlign={"center"}
          maxW={1200}
          bg={"gray.900"}
        >
          <Heading mb={3} size={"4xl"}>
            Vaults
          </Heading>
          <Text fontSize={{ lg: "22px", base: "20px" }} maxW={1000} mx={"auto"}>
            Boost your trading profits and find your edge from a range of
            diverse quant strategies. These techniques allow you to earn from
            bid-ask spreads while maintaining hedged, market-neutral positions.
          </Text>
        </Box>
        <Flex gap={5} wrap={"wrap"} py={8} px={4} justify={"center"}>
          {vaults &&
            vaults.length > 0 &&
            vaults?.map((vault, i) => (
              <VaultCard vault={vault} key={"vault" + i} />
            ))}
        </Flex>
      </main>
    </>
  );
}

export const getServerSideProps = async (ctx: GetServerSidePropsContext) => {
  return {
    props: {
      vaults,
    },
  };
};
