# AP Invoice Control — Demo Script (Mixed Audience, 30–35 min)

Audience: a mix of leadership/finance stakeholders and hands-on AP team members.
Goal: leadership sees the controls, risk-reduction and time savings; the AP team sees exactly how they'd use it day-to-day.

---

## Before you start

1. **Reset to clean data.** Open the app → **Master Data → Business Rules** tab → **Reset demo data** (red button at the bottom). Confirm. This wipes anything from your own testing and restores the seeded vendors/POs/agreements with zero invoices — you want a blank invoice register when the demo opens.
2. **Set the role to AP Maker** and the **User** field to a name your audience will recognise as "the preparer" (e.g. your own name, or "Aditi Rao" which is already seeded).
3. **Have one real-looking invoice image or PDF ready to upload** — this is what makes the AI extraction moment land. A screenshot of any sample invoice works; it doesn't need to be real. If you don't have one, a plain scanned bill or even a clearly-laid-out invoice template PDF is fine — the point is showing the AI reading an actual document, not the specific vendor.
4. **Open the file in its own browser tab**, full screen if possible, and close other tabs/notifications so the audience isn't distracted.
5. Know your one caveat going in (see "How to frame this honestly" below) so you're not caught off guard by the obvious question.

---

## How to frame this honestly (say this near the start)

> "This is a working prototype, not the final production system. Every control, validation rule and workflow you'll see actually runs — it's not mocked-up screens. What's *not* production-grade yet: it doesn't connect to our real ERP, vendor master, or GSTN filings — those are demo data you can edit live. The AI document-reading is real and calls Claude directly. Think of this as a proof of concept that shows exactly *what* the target system should do and how it should feel to use, so we can validate the design before committing engineering time to a full build."

Setting this expectation up front means nobody derails the demo later asking "does this update SAP" — you've already answered it.

---

## Section-by-section script

### 1. Open with the problem (2 min)
Don't open the app yet. Say what's broken today:
- Manual duplicate checks, PO matching done by eyeballing spreadsheets, exceptions tracked in email threads, no single register anyone can filter or export cleanly.
- Ask the room: "How long does it take us today to catch a duplicate invoice, or confirm a vendor's bank details haven't silently changed?" Let someone answer — it sets up the payoff.

### 2. Dashboard tour (3 min)
Open the app on **Dashboard**. It'll show the empty state since you just reset — that's fine, say so:
> "This is a clean register — as invoices flow through, this fills in automatically."
Point out what's *there* even empty: the filter row (vendor, PO/non-PO, status, date), and mention the KPI tiles and charts that populate once data exists (you'll return here at the end to show it live).

### 3. Create an invoice — Vendor & Invoice Details (3 min)
Click **+ New Invoice**. Walk the room through the wizard tracker at the top (six steps) — this is the structure, not just a form:
- Pick a vendor from the dropdown (**Sterling Industrial Supplies Pvt Ltd**) — point out it's tied to a Vendor Master, not free text.
- Fill invoice number, date, gross value, taxable value, CGST/SGST/IGST, total tax.
- Mention TDS/RCM fields exist for compliance completeness without dwelling on them.

**Talking point:** "Every field the AP team fills in manually today has a home here, structured — not a spreadsheet column that can be renamed or deleted by accident."

### 4. AI document extraction — the wow moment (4 min)
Click **3. Documents**. Upload your prepared invoice image under "Mandatory: invoice document."
- While it processes, narrate: "This isn't OCR-as-a-gimmick — it's sending the actual document to an AI model and asking it to read the invoice number, vendor, amounts and dates."
- When the comparison table appears, point at any row marked **"Differs"** — this is the AI's reading next to what was typed in. Click **Apply AI values to form** to show it can auto-correct in one click.

**Talking point for leadership:** "This is where re-keying errors get caught before they become payment errors — not after."

### 5. PO / Agreement matching (3 min)
Go back to **2. PO / Agreement**. Set PO Available = Yes, pick **PO-50025**.
- Point out the PO balance is tracked live — this invoice will be checked against real remaining balance, not just the original PO value.
- Mention Agreement matching works the same way for contract-based vendors, with contract period and total-value checks.

### 6. Run validation — the control layer (4 min)
Go to **4. Validation**, click **Run validation**. Walk through the categories as they render: Basic, Duplicate, Vendor, PO, Compliance.
- Call out anything that shows **WARNING** or **FAIL** and read the message aloud — this is the point: every check explains *why*, not just pass/fail.
- Point at the **Risk level** pill. Explain it aggregates the individual flags (duplicate, bank mismatch, PO overrun) into one signal for whoever's reviewing.

### 7. Duplicate detection — live "gotcha" (3 min)
This is worth staging deliberately: **before the demo**, submit one invoice fully through to at least "Submitted" status with a memorable invoice number (e.g. "INV-9001"). During the live demo, create a **second** invoice with the *same vendor and invoice number* and run validation.
- The duplicate check will show **FAIL** with the exact matching invoice referenced.
> "This is the check that today depends on someone remembering they already saw this invoice number. Here, it's automatic and it names the prior invoice."

### 8. Exceptions (3 min)
Go to **5. Exceptions**, click **Generate from validation failures** if any are open.
- Show the fields: severity, responsible person, resolution, and — for Critical severity — **Override approval**.
> "Critical exceptions can't be silently waved through. Someone named has to either resolve it properly or put their name against an authorized override. That's the audit trail leadership usually asks for after the fact — here it's built in up front."

### 9. Full approval workflow — three roles, one invoice (5 min)
This is the section to slow down for, since it's the part the AP team will recognise most and leadership cares most about controls.
1. As **AP Maker**, go to **6. Review & Workflow**, click **Submit for review**.
2. Switch **Role** to **AP Reviewer**. Go to **Validation Queue**, open the invoice, click **Move to Under Review**, re-run validation, then **Evaluate & route**.
3. Switch **Role** to **Approver**. Go to **Approvals**, open the invoice. Click **Approve** *without* changing the User field first — let it get blocked.
   > "Watch the bottom right." Read the toast aloud: *"Segregation of duties: the Approver cannot be the same person as the Preparer."*
   > "This is enforced in software, not by policy memo. Whoever prepared the invoice literally cannot also approve it."
4. Change the **User** field to a different name, click **Approve** again — it goes through.
5. Switch **Role** to **Finance Admin**, open the invoice, **Mark Posted**, then **Mark Paid**.

**Talking point:** "That's five people's worth of controls — maker, reviewer, approver, finance ops — enforced by the system, not by someone remembering the process."

### 10. Excel register export (2 min)
Go to **Invoice Register**, click **Export register to Excel**. Open the downloaded file live if you can.
- Show the multiple sheets: Invoice Register, Validation Details, Exceptions, Vendor Summary, Dashboard.
- Mention the frozen header row and filters are already applied — "this is ready to drop into a month-end pack, not a raw data dump."

### 11. Master Data & configurability (2 min)
Go to **Master Data → Business Rules**. Point at the price/quantity tolerance and PO-mandatory-threshold fields.
> "These aren't hard-coded. Finance can tune the tolerance for PO variances, or the ₹ threshold above which a PO becomes mandatory, without engineering involvement."
Briefly show the Vendors tab too — editable inline, this is where a real system would sync from SAP/Oracle/whatever ERP is in play.

### 12. Audit Trail (1 min)
Click **Audit Trail**. Scroll through the log entries generated just from this demo.
> "Every status change, every approval, every override is timestamped with who did it. This is what an auditor asks for, generated automatically instead of reconstructed after the fact."

### 13. Return to Dashboard — now it's alive (2 min)
Go back to **Dashboard**. Now that invoices exist, the KPIs and charts are populated.
> "This is the same dashboard you saw empty at the start — now showing real activity from the last 25 minutes."

### 14. Wrap-up and ask (2–3 min)
Close with the value recap in one breath:
> "In one invoice, you saw: AI-assisted data entry, duplicate detection, vendor and PO matching, MSME/GST compliance checks, segregation-of-duties enforcement, exception management with named accountability, a full audit trail, and an Excel register ready for month-end — all from one screen."

Then state the ask clearly (pick one):
- "I'd like feedback on which of these controls matter most to prioritize for a real build."
- "I'd like sign-off to scope this against our actual ERP and vendor master."
- "I want volunteers from the AP team to stress-test this against real (anonymised) invoices before we go further."

---

## Anticipated Q&A

**"Does this connect to [SAP / Oracle / Tally / our ERP]?"**
No — today it runs on demo data you can edit under Master Data. A real build would sync vendor, PO and GL data from the ERP instead of the seeded list.

**"Is the AI extraction actually reading the document, or is that faked?"**
It's real — it sends the uploaded file to an AI model and asks for structured fields back. No document, no extraction.

**"Where's the data stored — is this secure?"**
Right now it's a demo build with data stored locally to your account, not a production database. That's exactly why we're not using real invoices or real vendor bank details in this walkthrough.

**"Can we change the approval hierarchy / tolerances / who can override what?"**
The tolerances and PO threshold are already configurable (Business Rules tab). The role permissions themselves (who can do what) are currently fixed in this prototype — that would be a configuration screen in a production build.

**"What happens if two people are supposed to review, not just one?"**
Not modelled yet in this version — today it's Maker → Reviewer → Approver → Finance Admin, one person per stage. Multi-approver chains would be a real-build requirement to capture.

**"How long would a production version take?"**
Don't answer this on the spot with a number — that's a scoping conversation, not a demo answer. Say: "That depends on ERP integration scope, which is exactly the kind of thing we'd nail down in a follow-up."

---

## If something goes wrong live

- **A button seems unresponsive / nothing happens:** it's very likely a rule quietly blocking you (segregation of duties, missing document, unresolved critical exception) — check the bottom-right corner for a toast message that appears for ~3 seconds. Narrate it: "that's actually the control working, not a bug."
- **You want to rewind mid-demo:** there's no undo, but you can switch to **Master Data → Business Rules → Reset demo data** and restart the specific section — better to do this during a natural pause than to try to talk over a mistake.
- **AI extraction fails or times out:** don't panic-narrate. Say "let's give that a moment" and continue talking through the next field while it resolves, or move on and revisit — the rest of the demo doesn't depend on it succeeding.

