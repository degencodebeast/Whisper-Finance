import {
  Box,
  Button,
  FormControl,
  FormLabel,
  HStack,
  Input,
  Stack,
  Tab,
  TabList,
  TabPanel,
  TabPanels,
  Tabs,
  Text,
  useToast,
} from "@chakra-ui/react";
import { useFormik } from "formik";
import { ReactNode, useState } from "react";
import { CustomRadioGroup } from "../CustomRadioGroup";
export default function DepositOrWithdrawalBox({
  walletBalance = 0,
  walletToken,

  description,
}: {
  walletBalance: number;
  description?: string | ReactNode;
  walletToken: string;
}) {
  const [type, setType] = useState<"deposit" | "withdrawal">("deposit");

  return (
    <Box
      transition={"0.3s ease-out"}
      flex={1}
      minW={{ base: 300, md: 400, lg: 400 }}
      minH={380}
      border={"1px"}
      borderColor={"gray.600"}
      rounded={"xl"}
      maxW={{ lg: 450 }}
      mx={"auto"}
    >
      <Tabs
        onChange={(index) => {
          setType(index === 0 ? "deposit" : "withdrawal");
        }}
        display={"flex"}
        flexDir={"column"}
        h={"full"}
        isFitted
      >
        <TabList>
          <Tab>Deposit</Tab>
          <Tab>Withdraw</Tab>
        </TabList>
        <TabPanels flexGrow={1}>
          <TabPanel h={"full"}>
            <TradeTypeBox
              walletBalance={walletBalance}
              walletToken={walletToken}
              type={"deposit"}
            />
          </TabPanel>
          <TabPanel h={"full"}>
            <TradeTypeBox
              walletBalance={walletBalance}
              walletToken={walletToken}
              description={
                <>
                  <Text>
                    Withdrawals can be requested at any time and will be
                    available after 7 days. Profits will not be accrued during
                    the redemption period, while losses can still be incurred.
                  </Text>
                  <Text>
                    The maximum amount is after fees, while the final amount
                    received may differ from the amount requested.
                  </Text>
                </>
              }
              type={"withdrawal"}
            />
          </TabPanel>
        </TabPanels>
      </Tabs>
    </Box>
  );
}
export const TradeTypeBox = ({
  walletBalance,
  walletToken,
  description,
  type,
}: {
  walletBalance: number;
  description?: string | ReactNode;
  walletToken: string;
  type: "deposit" | "withdrawal";
}) => {
  const toast = useToast({
    duration: 3000,
    position: "top",
    title: "Successful",
    status: "success",
  });
  const [isInputFocus, setIsInputFocus] = useState(false);
  const formik = useFormik({
    initialValues: {
      amount: "" as number | string,
    },
    onSubmit: (values) => {
      formik.setSubmitting(true);

      if (type === "deposit") {
        setTimeout(() => {
          toast({
            status: "success",
            title: "Deposited successfully",
          });
          formik.setSubmitting(false);
          formik.resetForm();
        }, 2000);
      } else {
        setTimeout(() => {
          toast({
            status: "success",
            title: "Withdrawal request successful",
          });
          formik.setSubmitting(false);

          formik.resetForm();
        }, 2000);
      }
    },
  });
  const { values, handleChange, handleSubmit } = formik;

  function onInputFocus() {
    setIsInputFocus(true);
  }
  function onInputBlur() {
    setIsInputFocus(false);
  }

  function handleRadioChange(value: string) {
    formik.setFieldValue("amount", (+value * walletBalance) / 100);
  }

  return (
    <>
      {description && <Stack mb={5}>{description}</Stack>}
      <Stack
        as="form"
        justifyContent={"space-between"}
        minH={350}
        // @ts-ignore
        onSubmit={handleSubmit}
        h={"full"}
      >
        <Stack>
          <FormControl>
            <HStack justify={"space-between"}>
              <FormLabel>
                <Text as={"span"} textTransform={"capitalize"}>
                  {type}
                </Text>{" "}
                amount:
              </FormLabel>
              <Text as="span" color={"gray.300"} fontSize={"15px"}>
                Max: {walletBalance} {walletToken}
              </Text>
            </HStack>
            <HStack
              gap={4}
              border={"1px"}
              borderColor={isInputFocus ? "orange.500" : "gray.600"}
              rounded={"full"}
              px={3}
            >
              <Input
                type="number"
                h={"45px"}
                step="0.01"
                rounded={"none"}
                _focus={{
                  outline: "none",
                  boxShadow: "none",
                  borderColor: "orange.500",
                }}
                border={"none"}
                borderRight={"1px"}
                placeholder={walletBalance + ".00"}
                borderRightColor={"gray.600"}
                name="amount"
                onFocus={onInputFocus}
                onBlur={onInputBlur}
                value={values.amount}
                onChange={handleChange}
              />

              <Text as={"span"}>{walletToken}</Text>
            </HStack>
          </FormControl>
          <CustomRadioGroup
            options={["25", "50", "75", "100"]}
            getLabel={(value: string) => `${value === "100" ? "MAX" : value}`}
            onChange={handleRadioChange}
            initialValue={+formik.values.amount}
            totalAmount={walletBalance}
          />
        </Stack>
        <Button
          type="submit"
          isLoading={formik.isSubmitting}
          loadingText={
            type === "deposit" ? "Depositing..." : "Submitting request..."
          }
          size={"lg"}
          isDisabled={formik.values.amount === 0 || formik.values.amount === ""}
        >
          {type === "deposit" ? "Deposit" : "Request Withdrawal"}
        </Button>
      </Stack>
    </>
  );
};
