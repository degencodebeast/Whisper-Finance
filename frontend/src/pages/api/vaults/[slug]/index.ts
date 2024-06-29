import { vaults } from "@/lib/vaults";
import { Vault } from "@/types";
import { mainHandler } from "@/utils";

import { type NextApiRequest, type NextApiResponse } from "next";

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  return mainHandler(req, res, {
    GET,
  });
}
export async function GET(req: NextApiRequest, res: NextApiResponse) {
  try {
    const { slug } = req.query as { slug: string };
    const vault = vaults.find((v) => v.slug === (slug as string));
    res.status(200).json({
      data: vault,
      success: true,
      message: "Vault retrieved successfully",
    });
  } catch (error) {
    res.status(500).json({ error, message: "Something went wrong..." });
  }
}
