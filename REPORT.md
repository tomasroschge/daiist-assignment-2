# Assignment 2 Report

- **Name**: Tomás Roschge
- **Student ID**: 19045
- **Email**:troschge.ieu2022@student.ie.edu
- **Group**: BBADBA 5A

## Business problem, and the cost of being wrong

At a mid-sized spruce sawmill in Central Europe, every board is inspected at the end of the planingn line. Two human graders look at each board and decide on its grade. The board can move on to the premium grade, which is then sold to furniture and panelling manufactureres who need clean visible surfaces, or to the standard grade, sold at a lower price for construction, pacakging and pallets, as appearence does not matter. The model supports this decision: from a camera image of the board, it flags whether the board has a defect that disqualifies it from the premium grade. Clear cases are sorted automatically and borderline cases are sent to a grader.

### What counts as positive
I treat a board section as **positive (fails premium grade)** if it contains at least one attribute that would make the furniture customer reject the board. This can be by because:
1. It weakens the board or can fall out; cracks, dead or missing knots.
2. It ruins the finish: resin pockets, which bleed through paint
3. It discolours or ruins the visible surface of the board.

A board is **negative (acceptable for premium)** if it has no defect, or only sound, intergrown knots or minor irregularities. These are part of the natural look of spruce, and visual grading rules allow them within limits.

I define "positive" as "has a disqualifying defect" because that is the event the model must detect and classify.

### Three outcomes

The model gives each board section a score: the highest confidence among all disqualifying defects it detects in the image. Two thresholds split that score into three outcomes:

- **Pass** (score below the lower threshold): the board goes straight to the premium stack, without human inspection.
- **Review** (score between the two thresholds): diverts the board to a side conveyor, where a grader inspects the physical board, and decides the grade. I assume about **10 seconds** per board, compared with the **2–3 seconds** a grader has today to judge a board at full line speed. We take it off the main line so the review does not slow the line down.
- **Fail** (score above the upper threshold): the board goes straight to the standard-grade stack, without human inspection.

Today, the graders judge every board. With the model, only the boards in the review band are inspected, so the question becomes whether that band is small enough for them to keep up (see step 7).

### The cost of being wrong

The costs are measured against a perfect grader: the cost of an outcome is the extra money that the company loses compared with sending every board to its correct grade. That is why a true positive (a defective board correctly downgraded) and a true
negative (a good board correctly sold as premium) both cost **€0**: each board is sold at the price it deserves.

**Board assumed**: planed spruce board, 25 × 150 mm × 4.0 m ≈ **0.015 m³**.

- **False positive** (a good board is downgraded to standard). The sawmill sells it at the standard price instead of the premium price.
  - Standard spruce price: about **€310/m³**. This is the 44–50 × 150 mm spruce price in Germany in December 2025 (€305–325/m³, Fastmarkets).
  - Premium visual-grade price: about **€372/m³**. I took the standard price and applied a +20% grade premium, which is the price ratio between "unsorted" (joinery quality) and "fifths" for the same 25 × 100 mm planed board at a UK timber merchant (£4.49 vs £3.74 per metre ex VAT). Retail prices are much higher than wholesale, so I use only the ratio, not the absolute price.
  - FP cost = (372 − 310) × 0.015 ≈ **€0.93 per board**.

- **False negative**:
  - Replacement premium board: 372 × 0.015 ≈ €5.60
  - Claim handling and admin: ~20 min of sales/quality staff × ~€25/h ≈ **€8**
  - Share of return freight and repackaging: €150 return shipment shared across ~30 boards in a typical claim ≈ **€5**
  - Goodwill discount and risk to the account: a 2–3% discount on a ~€200 package ≈ **€5**
  - FN cost ≈ **€24 per board**.

- **Human review**: **assumed** 10 seconds per board × €20/hour fully loaded
  labour cost ≈ **€0.06 per board reviewed**

A false negative is about **25 times** as costly as a false positive (€24 vs €0.93). The most uncertain figures are the visual-grade premium and the goodwill component of the FN. I will test how the threshold changes if the ratio is anywhere between 10× and 50×.


### Volume and base rate
Modern planer mills with automatic grading run 75–240 boards per minute, and at those speeds manual grading is close to impossible. A mill that still grades by hand runs slower, so I assume **40 boards per minute**, over two shifts of 7.5 productive hours: about **36,000 boards a day**, checked today by two graders.

Most boards do not reach the premium visual grade: it is the minority, high-value share of the output. Clear grades are only about 5% of spruce lumber in one study of Alaskan Sitka spruce. I expect a large share of boards to have at least one disqualifying defect. I fix the exact base rate in the cost section.

### What this means for the rest of the project
Because a missed defect costs about 25 times as much as a downgraded good board, I care more about **recall** on the disqualifying defects than about overall accuracy or mAP. This pushes the threshold lower: I would rather downgrade
or review a good board than let a defect through. The limit is people: with only two graders, it is not realistic that they will review a large portion of a line running at 40 boards per minute, so the review band has to stay small.

## Dataset

**Roboflow Universe**: workspace `defect-detection-w4mv8`, project
`wood-defect-detection-9w3x4`, **version 6**
(https://universe.roboflow.com/defect-detection-w4mv8/wood-defect-detection-9w3x4/dataset/6).
Object detection, CC BY 4.0. Used as published, not forked.

**Origin.** This Roboflow project is a 3,258-image subset of a public dataset of wood surface defects collected by VSB – Technical University of Ostrava (Czech Republic) on an active sawmill production line (Kodytek, Bodzas and Bilik, *F1000Research* 2022). The images were taken by an industrial line-scan colour camera with LED lighting while boards moved along the conveyor. The authors describe the material only as sawn timber and do not name the species. The images show a light-coloured softwood consistent with spruce, which is the assumption of my business case.

**What one image represents.** An image is a section of the surface of one board as it can be seen from above by a camera. Each defect is marked with a bounding box and one of 10 dffect distinct classes. Images with no boxes are defect-free boards. For the analysis, I treat ne image as one board. 

**Classes and how they map to my business case.**

| Dataset class | What it is | My label |
|---|---|---|
| Crack | crack in the wood | **positive** |
| Dead_Knot | dead, loose knot | **positive** |
| Knot_missing | hole left by a knot that fell out | **positive** |
| knot_with_crack | knot with cracks around it | **positive** |
| Marrow | pith (centre of the log) | **positive** |
| resin | resin pocket | **positive** |
| Blue_Stain | fungal blue discolouration | **positive** |
| Live_Knot | sound, intergrown knot | negative (acceptable) |
| Quartzity | grain irregularity | negative (acceptable) |
| overgrown | — | excluded (see next section) |

A board is **positive** if it contains at least one box that belogns to the positive class. he image's score is the highest confidence the mode gives to any positive class detection. Live knots and quarzity do not make a board fail. Never.

*Why this dataset serves the problem rather than merely resembling it.**
1. **Same view as production site.** The images come from a camera over a real sawmill conveyor, which is exactly where the model owudl be useful.
2. **The classesmatch the business decision.** the dataset separates and distinguishes between live knots from dead ones. It also labels cracks, resin, and blue stain separately. The business case I am proposing depends on these differences: a single deffect could not tell an acceptable knot from a disqualifying one.
3. **Defect-free boards are labelled.** Clean boards appear as images with no boxes. These are the negatives needed to measure false positives (the cost of downgrading good boards).

## What the dataset's composition implies

**Split sizes.** Train has 1,733 images, test has 1,525 and **valid has 0**. Training needs a validation set, so I hold out 15% of train with a fixed random seed and leave test untouched.

**Instances per class.**

| Class | Train | Test | My label |
|---|---|---|---|
| Live_Knot | 2,108 | 288 | negative |
| Dead_Knot | 926 | 299 | positive |
| resin | 313 | 236 | positive |
| knot_with_crack | 130 | 108 | positive |
| Crack | 82 | 465 | positive |
| Marrow | 83 | 4 | positive |
| Quartzity | 81 | 34 | negative |
| Knot_missing | 48 | 73 | positive |
| Blue_Stain | 26 | 75 | positive |
| overgrown | 2 | 0 | excluded |

**Images by my business rule.**

| | Train | Test |
|---|---|---|
| Positive (at least one disqualifying defect) | 1,033 (59.6%) | 592 (38.8%) |
| Negative: only live knots / quartzity | 700 (40.4%) | 141 (9.2%) |
| Negative: no defect at all | **0 (0%)** | **792 (51.9%)** |

**Object size.** Defects are small: the median box covers about 0.3% of the image. YOLO resizes the longest side to 640 px, so a typical defect ends up about 21 × 21 px, and the smallest 10% of resin pockets and missing knots end up around 8–12 px.

**What this implies.**
1. **Test does not look like train.**
   - Every test image is rotated 90° (704 × 1,924, board vertical), while every train image is in the original camera orientation (2,800 × 1,024, board horizontal).
   - All 792 defect-free boards are in test, and train has none.
   - Test has 5.7 times more cracks than train (465 vs 82).
   A model trained on train is therefore evaluated on images that differ in orientation and in mix. A drop in the test performance may come from this, not from the model's ability to see defects.
2. **Some per-class numbers are too thin to trust.**
   - **Overgrown** (2 examples, none in test) is excluded.
   - **Marrow** has only 4 test instances, so its precision and recall mean nothing.
   - **Blue_Stain** (26 train instances in 17 images) and **Knot_missing** (48) give the model very little to learn from.
   - **Crack** is the most worrying: it is a key disqualifying feature, but the model is tested on 465 examples while it oonly learns from 82
3. **Small objects favour a larger input size.** At 640 px the smallest defects are only a few pixels wide. This is an argument for training at 1,280 px.
4. **Test composition is not production composition.** On the real line, about 90% of board images have at least one defect (18,283 of 20,275 in the original data), whereas in test only 48% do. So it would not make sense to read the expected cost directly off test, which is why I measure error rates on test and reweight them to the production base rate.
5. **What I cannot conclude.**
   - Nothing reliable about Marrow, Blue_Stain or Knot_missing on their own.
   - Results only hold for this camera and this lighting.
   - The headline decision ("does the board have any disqualifying defect?") uses all positive classes together, so it is much more stable and reliable than any single class.

## Finetuning and baselines

*Which model and task (detection or classification) and why. A results table on
the same test split: your finetuned model, the pretrained COCO model zero-shot,
and a trivial baseline. What changed, and whether the gap is as large as you
expected.*

## Per-class evaluation and failure modes

*Per-class AP50, or per-class precision/recall and the confusion matrix.
Which class carries the headline number, which one is dragging, and what the
model actually confuses with what. Show where it breaks, not just that it
works.*

## Cost matrix and operating point

*Your euro cost for each kind of error and where each figure came from. The
base rate you assumed. The cost-against-threshold sweep, and the operating
point you chose. State the assumption that would most change your answer if it
were wrong.*

## What a person still has to check

*Your two thresholds, and what share of cases they send to a person. How many
that is per day, how long one takes to check, and how many people that needs.
Is that realistic? Then your design priced against the three alternatives:
doing nothing, having a person check everything, and letting the model decide
on its own.*

## Limitations & next steps

*Real limitations you found, and concretely how you'd address each one with
more time or data. Not generic hedging.*

## Generative AI use disclosure

*Per the syllabus AI Policy: what you used and how, or "no AI content used."*
