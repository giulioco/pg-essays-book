# Printing your copy on Lulu

This guide covers two ways to get from `out/` to a printed book at your door: do it yourself in about 15 minutes, or hand the job to an AI agent that can use a browser.

Lulu prints one copy at a time with no minimum order. In November 2026, a 495-page copy cost about **$14 in paperback** or **$23 in hardcover**, plus US shipping from about $6.

> **Before you start:** run `python3 build.py`. It writes `out/interior.pdf`, `out/cover.pdf` and `out/ORDER.md`. `ORDER.md` lists the exact values for your build (page count, cover size), so keep it open while you go.

---

## Option A: an AI agent does it for you

Use any agent that can control a web browser, such as Claude with Claude in Chrome, Claude Code with browser tools, or ChatGPT agent mode. It also needs to read files on your computer: the agent uploads two PDFs, and it may need to rebuild the cover once.

Sign in to lulu.com yourself first. Then paste the prompt below. The agent stops before payment, so you review the order and press **Pay** yourself.

````text
You are helping me order ONE printed copy of a book I built for my own personal use,
using Lulu (lulu.com). I am already signed in to Lulu in the browser.

Files (in the repo folder I'm working in):
- out/interior.pdf  : the book block, 6x9 in trim (pages are 6.25x9.25 in incl. bleed)
- out/cover.pdf     : one-piece wraparound cover (back + spine + front, with bleed)
- out/ORDER.md      : the exact settings for this build. Read it first.
- build.py          : rebuilds the cover at an exact size: python3 build.py --cover WIDTHxHEIGHT

Binding I want: PAPERBACK (Perfect Bound)    <- change to HARDCOVER (Case Wrap) if you prefer
Ship to: I will enter the address myself at checkout.

Rules:
- This is personal printing. Never choose retail sales, global distribution, Lulu
  Bookstore listing, Lulu Direct, a public/shareable link, or a free ISBN.
  The project must stay private.
- Do not create accounts, change account settings, enter passwords, or enter payment details.
- Stop and ask me if anything on screen doesn't match these steps or looks like it
  will cost money beyond one copy plus shipping.
- Take a screenshot after each major step so I can follow along.

Steps:
1. Go to https://www.lulu.com/create/print-books and start a new Print Book project.
2. When asked for the goal, choose "Print Copies for Your Own Use" (personal printing,
   no ISBN, not for sale). Title: exactly the title in out/ORDER.md ("Essays").
   Language: English. Pick any sensible category (e.g. Business / Essays).
3. Copyright/details step: author/contributor = the author in out/ORDER.md.
   Do NOT request an ISBN. Leave optional fields empty.
4. Design step:
   a. Upload out/interior.pdf as the interior file. Confirm Lulu detects US Trade 6 x 9 in
      and the page count from out/ORDER.md. If Lulu warns about size or bleed, stop and tell me.
   b. Set the specs from out/ORDER.md: Standard Black & White, 60# Cream Uncoated,
      the binding above, Matte cover finish.
   c. In the cover section choose to upload your own cover. Read the exact cover dimensions
      Lulu requires (shown in the requirements box / "Download Template").
      Compare with the size in out/ORDER.md. If they differ by more than 0.01 in
      (always the case for hardcover), run:  python3 build.py --cover WIDTHxHEIGHT
      using Lulu's numbers in inches, then use the new out/cover.pdf.
   d. Upload out/cover.pdf.
   e. Open the preview. Check that the spine text sits inside the spine, the front cover
      title is not near the trim, and interior pages have no white borders or warnings.
      Show me screenshots of the cover preview.
5. Finish the remaining steps with the minimum required input. Keep everything private
   ("Print Copies for Your Own Use" or "Private Access"; never retail/distribution).
   Complete/publish the project only as the private personal project.
6. Go to My Projects, open the project, and click "Add to Cart" (author price).
   Quantity 1.
7. Go to the cart and continue through checkout up to the shipping-method choice.
   Let me enter my address. Suggest the cheapest tracked shipping option.
8. STOP before payment. Summarize: binding, page count, price per book, shipping,
   tax, total. I will enter payment and click Pay myself.
````

---

## Option B: do it yourself

Lulu's site changes from time to time, so the labels below may differ slightly. The values to enter won't.

1. **Start the project.** Go to [lulu.com/create/print-books](https://www.lulu.com/create/print-books) and click **Start your Print Book**.
2. **Choose the goal: "Print Copies for Your Own Use".** This keeps the book private. It needs no ISBN and no tax forms, and it isn't listed for sale.
3. **Enter the details.**
   - **Title:** `Essays`. It must match the files.
   - **Author:** `Paul Graham`.
   - **ISBN:** skip it.
4. **Design step.**
   1. Upload `out/interior.pdf`. Lulu should detect **US Trade 6 × 9 in** and the page count.
   2. Pick the specs:
      - **Interior color:** Standard Black & White
      - **Paper:** 60# Cream
      - **Binding:** Paperback Perfect Bound or Hardcover Case Wrap
      - **Cover finish:** Matte
   3. Under the cover section, choose to **upload your own cover**. Lulu shows the exact cover size it needs.
   4. Check the size against `out/ORDER.md`:
      - **Paperback:** it should already match.
      - **Hardcover**, or any mismatch: rebuild the cover with Lulu's numbers in inches (the size below is only an example).
        ```bash
        python3 build.py --cover 14.85x10.5
        ```
   5. Upload `out/cover.pdf`, then open the **preview**.
5. **Finish the project.** Fill only what's required, and keep it private. Never choose retail or global distribution.
6. **Order a copy.** Go to **My Projects**, open the book, click **Add to Cart**, and **Checkout**. Ordering from My Projects charges the author price, which is the cost of printing.

**Tip:** for your first copy, choose the cheapest shipping and look over the proof copy before you order more or gift any. You can cancel an order within about an hour of placing it, from your order history.

---

## Troubleshooting

| Problem | What to do |
|---|---|
| Lulu says the cover size is wrong | Run `python3 build.py --cover WxH` with the exact size Lulu shows, then upload the cover again. |
| Lulu says the interior has no bleed or the wrong size | The interior should be 6.25 × 9.25 in. Rebuild with `python3 build.py` and upload `out/interior.pdf` again. |
| The page count changed after you edited `essays.json` | Upload both PDFs again. The spine width depends on the page count. |
| Hardcover spine width | It comes from a lookup table in Lulu's template, not a formula. Always use Lulu's number with `--cover`. |
