import DataList from "@/components/DataList";
import DepositOrWithdrawalBox from "@/components/DepositOrWithdrawalBox";
import HeaderNav from "@/components/HeaderNav";
import { LineDivider } from "@/components/LineDivider";
import MarkdownRenderer from "@/components/MarkdownRenderer";
import SectionHeading from "@/components/SectionHeading";

import VaultChart from "@/components/VaultChart";
import { useCustomSign, useUserBalance } from "@/hooks";
import { vaults } from "@/lib/vaults";
import { Vault } from "@/types";
import {
  Box,
  Flex,
  HStack,
  Heading,
  Image,
  ResponsiveValue,
  Stack,
  Tab,
  TabList,
  TabPanel,
  TabPanels,
  Tabs,
  Text,
} from "@chakra-ui/react";
import { useConnection, useWallet } from "@solana/wallet-adapter-react";
import axios from "axios";
import { GetServerSidePropsContext, InferGetServerSidePropsType } from "next";
import { Router, useRouter } from "next/router";
import { useEffect, useState } from "react";

export default function VaultPage({
  vault,
}: InferGetServerSidePropsType<typeof getServerSideProps>) {
  // const { balance } = useUserBalance();
  // console.log({ balance });
  const { connection } = useConnection();
  const { signed } = useCustomSign();
  const { publicKey, connecting, connected } = useWallet();
  const router = useRouter();
  if (!vault) router.reload();
  const [balance, setBalance] = useState<number | null>(null);
  console.log({ balance, signed, publicKey, connecting, connected });

  useEffect(() => {
    if (publicKey && signed) {
      connection
        .getBalance(publicKey, "max")
        .then((balance) => setBalance(balance));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [publicKey]);
  const walletBalance = 0;
  const walletToken = "USDC";
  const tabBtnStyle = {
    fontSize: { xl: "24px", base: "16px", md: "20px" },
    border: { sm: "2px" },
    borderColor: { sm: "transparent" },
    _hover: {
      bg: "orange-rgba.100",
      color: "orange.400",
      borderColor: "orange-rgba.200",
    },
    rounded: { sm: "full", base: "md" },
    color: "gray.400",
    fontWeight: 400,
    _selected: {
      color: "white",
      bg: "orange.500",
      borderColor: "transparent",
      _hover: {
        borderColor: "transparent",
        bg: "orange-rgba.500",
        color: "white",
      },
    },
    w: { base: "full", sm: "auto" },
    flexShrink: { base: 0, sm: 1 },
    px: { lg: 6, base: 3, md: 4 },
  };
  const tabPanelsContainerStyle = {
    px: 1,
    display: "flex",
    flexWrap: { base: "wrap", lg: "nowrap" } as ResponsiveValue<
      "wrap" | "nowrap"
    >,
    w: "full",
    gap: 10,
    py: 8,
  };
  const tabPanelStyle = {
    flex: 1,
    px: 0,
    minW: { sm: 450, md: 480, lg: 500, xl: 600, base: 320 },
  };
  const vaultPerformanceData = {
    " Total Earnings (All Time)": "  $2,903,690.85",
    " Cumulative Return": "40.65%",
    APY: "0.95%",
    "Max Daily Drawdown": "-0.87%",
    "30D Volume": "$250,698,411.18",
  };

  const yourPerformanceData = {
    "Total Earnings (All Time)": "$0.00",
    "Your Cumulative Net Deposits": "$1.15",
    "Your Balance": "$1.14",
    ROI: "0.0000%",
    "Vault Share": "0%",
    "Max Daily Drawdown": "0.00%",
  };
  const yourFeesBreakdown = {
    "Profit Share Fees Paid": "$0.00",
    "High-Water Mark": "$1.15",
  };
  const yourTransactionHistory = { "Deposited 1.15 USDC": "08 Jun 2024" };
  return (
    <>
      <HeaderNav />
      <Box as="main" mx={"auto"} maxW={"1350"}>
        {vault && vault?.slug === "bonking-dragon" && (
          <HStack
            maxW={1300}
            justify={"flex-end"}
            py={4}
            px={{ lg: 6, base: 4 }}
          >
            {" "}
            <Image
              alt=""
              src={vault?.mentions?.["bonk"]}
              w={"45px"}
              h={"45px"}
            />
          </HStack>
        )}
        <Box
          textAlign={"center"}
          py={{ lg: 12, base: 8 }}
          px={4}
          mt={10}
          bg={`#000b url(${
            vault?.cover || "/images/pattern.jpg"
          }) center / cover no-repeat`}
          backgroundBlendMode={"darken"}
        >
          <Heading size={{ sm: "3xl", base: "2xl" }} mb={4}>
            {vault?.name}
          </Heading>
          <Text
            fontSize={{ sm: "22px", base: "20px" }}
            color={"gray.300"}
            maxW={1000}
            mx={"auto"}
          >
            {vault?.intro}
          </Text>
        </Box>
        <HStack
          wrap={{ base: "wrap", sm: "nowrap" }}
          gap={{ lg: 10, base: 5, md: 8 }}
          justify={"center"}
          px={4}
          py={10}
        >
          <Stack align={"center"}>
            <Text
              as={"span"}
              fontFamily={"var(--font-comfortaa)"}
              fontWeight={600}
              fontSize={{ md: "35px", sm: "30px", base: "28px" }}
            >
              $25,865,348.01
            </Text>
            <Text as={"span"} color={"gray.300"} fontSize={"17px"}>
              Total Value Locked
            </Text>
          </Stack>

          <LineDivider
            styleProps={{
              w: { base: "100%", sm: "2px", md: "3px" },
              h: { base: "2px", sm: "55px" },
              flexShrink: 0,
            }}
          />
          <Stack align={"center"}>
            <Text
              fontFamily={"var(--font-comfortaa)"}
              as={"span"}
              fontWeight={600}
              fontSize={{ md: "35px", sm: "30px", base: "28px" }}
            >
              $30,000,000.00
            </Text>
            <Text as={"span"} color={"gray.300"} fontSize={"17px"}>
              Max Capacity
            </Text>
          </Stack>
        </HStack>
        <Flex
          mx={"auto"}
          justify={"center"}
          w={"full"}
          maxW={"1300"}
          px={{ lg: 8, md: 6, sm: 4 }}
        >
          <Tabs
            display={"flex"}
            flexDir={"column"}
            // w={"full"}
            mx={"auto"}
            colorScheme="orange"
            variant={"solid-rounded"}
            px={{ base: 2, lg: 3 }}
          >
            <TabList
              maxW={"fit-content"}
              flexWrap={{ base: "wrap", sm: "nowrap" }}
              justifyContent={{ base: "center" }}
              gap={{ lg: 8, base: 4, sm: 6 }}
              border={"1px"}
              rounded={{ sm: "full", base: "md" }}
              borderColor={"gray.600"}
              pos={"relative"}
              mx={"auto"}
              mb={8}
            >
              <Tab {...tabBtnStyle}>Vault Performance</Tab>
              <Tab {...tabBtnStyle}>Your performance</Tab>
              <Tab {...tabBtnStyle}>Overview</Tab>
            </TabList>
            <TabPanels {...tabPanelsContainerStyle}>
              <TabPanel {...tabPanelStyle}>
                <Stack gap={5} flex={1}>
                  <SectionHeading
                    title="Performance Breakdown"
                    containerStyleProps={{ mt: 0 }}
                  />
                  <DataList data={vaultPerformanceData} />
                  <Box>
                    <SectionHeading title="Cumulative Performance" />

                    <VaultChart />
                  </Box>
                  <SectionHeading title="Vault Details" />
                </Stack>
              </TabPanel>
              <TabPanel {...tabPanelStyle}>
                <Stack gap={5}></Stack>
                <Box>
                  <SectionHeading
                    title="Summary"
                    containerStyleProps={{ mt: 0 }}
                  />
                  <HStack
                    my={6}
                    divider={<LineDivider styleProps={{ w: "2px" }} />}
                    justify={"space-around"}
                  >
                    <Stack fontSize={"18px"} textAlign={"center"}>
                      <Text
                        as="span"
                        fontSize={{ base: "20px", md: "22px" }}
                        fontWeight={700}
                        fontFamily={"var(--font-comfortaa)"}
                      >
                        $0.0
                      </Text>
                      <Text as="span" color={"gray.300"}>
                        Your Balance
                      </Text>
                    </Stack>
                    <Stack fontSize={"18px"} textAlign={"center"}>
                      <Text
                        as="span"
                        fontSize={{ base: "20px", md: "22px" }}
                        fontWeight={700}
                        fontFamily={"var(--font-comfortaa)"}
                      >
                        $0.00
                      </Text>
                      <Text as="span" color={"gray.300"}>
                        Total Earnings (All Time)
                      </Text>
                    </Stack>
                  </HStack>
                </Box>
                <Box>
                  <SectionHeading title="Performance Breakdown" />
                  <DataList data={yourPerformanceData} />
                </Box>
                <Box>
                  <SectionHeading title="Fees Breakdown" />
                  <DataList data={yourFeesBreakdown} />
                </Box>
                <Box>
                  <SectionHeading title="Transaction History" />
                  <DataList data={yourTransactionHistory} />
                </Box>
              </TabPanel>
              <TabPanel {...tabPanelStyle}>
                <Stack gap={6}>
                  <Box>
                    <SectionHeading
                      title="Strategy"
                      containerStyleProps={{ mt: 0 }}
                    />
                    {/* <Stack gap={4}>
                      <Text>
                        Supercharger vault employs a delta-neutral market making
                        and liquidity provision strategy, primarily on Drift
                        perpetual swaps. The strategy edge is in advanced
                        volatility and inventory management models and a
                        superior on-chain infrastructure setup.
                      </Text>
                      <Text>
                        <Text as={"strong"} fontWeight={700}>
                          The strategy is built on a smart contract, meaning
                          funds cannot be withdrawn by anyone but you.
                        </Text>
                      </Text>
                    </Stack> */}
                    <MarkdownRenderer markdown={vault?.strategy as string} />
                  </Box>
                  <Box>
                    <SectionHeading title="Risks" />
                    <MarkdownRenderer markdown={vault?.risk as string} />
                  </Box>
                  <Box>
                    <SectionHeading title="Lock Up Period & Withdrawals" />
                    <Stack gap={4}>
                      <Text>
                        Deposited funds are subject to a 7 days redemption
                        period.
                      </Text>
                      <Text>
                        Withdrawals can be requested at any time. Funds will be
                        made available for withdrawal at the end of the
                        redemption period.
                      </Text>
                    </Stack>
                  </Box>
                  <Box>
                    <SectionHeading title="Fees" />
                    <Stack gap={4}>
                      <Text>A performance fee of 30% applies.</Text>
                      <Text>
                        For deposits over $250,000, contact us to learn more
                        about our White Glove service.
                      </Text>
                    </Stack>
                  </Box>
                </Stack>
              </TabPanel>
              <TabPanel
                flex={1}
                px={0}
                minW={{ md: 400, base: 300 }}
                display={"block!important"}
              >
                <DepositOrWithdrawalBox
                  walletToken={walletToken}
                  walletBalance={walletBalance}
                />
              </TabPanel>
            </TabPanels>
          </Tabs>
        </Flex>
      </Box>
    </>
  );
}

export async function getServerSideProps(ctx: GetServerSidePropsContext) {
  const { slug } = ctx.query;

  const vault = vaults.find((v) => v.slug === (slug as string));
  return {
    props: {
      vault,
    },
  };
}
