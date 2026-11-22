# Printing your copy on Lulu

Lulu prints one copy at a time with no minimum order. In November 2026, a 495-page copy cost **$14.37 in paperback** or about **$23 in hardcover**, plus US shipping from about $6.

> **Before you start:** run `python3 build.py`. It writes `out/interior.pdf`, `out/cover.pdf` and `out/ORDER.md`. `ORDER.md` lists the exact values for your build (page count, cover size), so keep it open while you go.

**Want an AI agent to do this for you?** Use the prompt in the [README](README.md#the-fastest-way-let-an-ai-agent-do-it). It follows the same steps as below and stops before anything personal or paid.

## Step by step

The labels below match Lulu's site in November 2026.

1. **Start the project.** Sign in to lulu.com, open [lulu.com/create/print-books](https://www.lulu.com/create/print-books) and click **Start Making My Print Book**.
2. **Start step.**
   - **Product type:** Print Book.
   - **Goal:** **Print Your Book**, which means "Upload your Book files to your account and purchase copies". Don't pick "Publish Your Book": that one is for retail sales.
   - **Project Title:** `Essays`.
   - **Book language:** English.
   - **Book category:** required; choose *Business & Economics*.
   - Click **Design Your Project**.
3. **Design step.**
   1. Under **Interior File Upload**, upload `out/interior.pdf`. Lulu shows the page count once it's processed.
   2. **Book Size:** **US Trade (6 x 9 in / 152 x 229 mm)**. A "Please select a Book Size" note may stay on screen even after you pick it; it doesn't block anything.
   3. **Interior Color:** Standard Black & White.
   4. **Paper Type:** 60# Cream — Uncoated.
   5. **Binding Type:** Paperback Perfect Bound or Hardcover Case Wrap.
   6. **Cover Finish:** Matte. The **Print Cost** updates as you choose.
   7. Under **Upload Your Cover**, read the required **Dimensions**:
      - **Paperback:** they match `out/ORDER.md` (for example *13.425 x 9.25 in, spine 1.175 in*).
      - **Hardcover**, or any mismatch: rebuild the cover with Lulu's numbers in inches. The size below is only an example.
        ```bash
        python3 build.py --cover 14.85x10.5
        ```
   8. Upload `out/cover.pdf`.
   9. In **Book Preview**, check two things: the cover text sits inside the shaded safety zones, and the spine title sits between the dotted fold lines.
4. **Review.** Click **Review Book** and check the specs. Then click **Confirm and Publish**. Under the "Print Your Book" goal, this only saves the project to your account. It isn't listed or sold anywhere.
5. **Order.** Click **Add to Cart**, then go to the **cart** and click **Checkout**. Then:
   1. Enter your shipping address.
   2. Choose a shipping method. Mail is the cheapest at about $6.
   3. Pay.

   To order again later, go to **My Projects**, open the project, and click **Add to Cart**. That charges the author price, which is the cost of printing.

**Tips:**
- Before ordering more or gifting any, get a single copy and check it.
- You can cancel an order within about an hour of placing it, from your order history.

## Troubleshooting

| Problem | What to do |
|---|---|
| Lulu says the cover size is wrong | Run `python3 build.py --cover WxH` with the exact size Lulu shows, then upload the cover again. |
| Lulu says the interior has no bleed or the wrong size | The interior should be 6.25 × 9.25 in. Rebuild with `python3 build.py` and upload `out/interior.pdf` again. |
| The page count changed after you edited `essays.json` | Upload both PDFs again. The spine width depends on the page count. |
| Hardcover spine width | It comes from a lookup table in Lulu's template, not a formula. Always use Lulu's number with `--cover`. |
| A "Performing security verification" page appears at checkout | It's Lulu's bot check. Wait a few seconds; it usually clears on its own. |
