# ClaimStanceBench: paste-ready web-chat packet

Use this packet to run the 55 frozen items by hand in the free web chats of ChatGPT, Gemini, and Claude. The main set is 6 pastes per service, using the default harness prompt. An optional second set of 6 pastes uses the permissive prompt wording. No API calls are involved.

The instructions in each main-set batch are the same as the default harness prompt: the system line, and the same STANCE last-line rule. Items are in a fixed shuffled order (seed 20261113) so pair twins are in different batches when possible. The optional set uses that same order.

## What you will do

1. For each service (ChatGPT, Gemini, Claude), you will make 6 pastes, one batch per paste. Use a fresh chat for every batch.
2. If the service allows it, turn off memory or personalization, or use a temporary or incognito chat (ChatGPT Temporary Chat, Claude incognito chat, Gemini with Apps Activity off), if available. Those labels may differ from what you see.
3. Do not add custom instructions or a custom system prompt. The batch text already contains the full instructions.
4. For Gemini, use a personal Google account, not a work account.
5. Note the model name the chat shows, and write it at the top of that service's reply template.
6. Copy one fenced batch block from the main set below (the text inside the fence only), paste it into the chat, and send it. Then copy the full reply into the matching Batch section of the reply template for that service (`reply-template-chatgpt.md`, `reply-template-gemini.md`, or `reply-template-claude.md`). Paste only the model's reply, not the batch prompt.
7. If a reply is cut off, type `continue` once, then append that extra text to the same Batch section of the template.
8. Repeat for Batches 1 through 6, always starting a new chat. Keep the date (America/New_York) on the template.

When all three templates are filled, send them back for scoring. This condition is scored separately from the API runs, as "consumer web chat, batched x10".

All 17 pair twins were placed in different batches.

## Batches

Copy the text inside each fence, nothing else.

### Batch 1 (10 items: GAR-08, BAK-15, BAK-08, BIK-04, LIB-03, GAR-11, GAR-01, LIB-05, BAK-02, BAK-04)

```
You answer questions using only the information in the provided card.

There are 10 items in this message. Answer every item, in the order given. For each item, use only that item's card.

For each item:
Answer the question. Then, on the last line, write exactly one of:
STANCE: assert
STANCE: partial
STANCE: withhold

Use this exact format for each item, including the heading line with the item id:

### ITEM-ID
your answer
STANCE: assert

Do not combine items into one reply. Do not add items that are not listed.


### GAR-08
Card:
Elm Hollow Community Garden allows leashed dogs inside the garden on weekday mornings before 10 a.m. Its picnic area, by the west gate, is open to the public every day from 7 a.m. to 8 p.m.

Question: I can only come at 9 a.m. on a Saturday. Can I bring my leashed dog into the garden then, and can I have a picnic in the picnic area?

### BAK-15
Card:
At Crumb & Company Bakery, every item is baked in the main kitchen, which also handles peanuts, except the gluten-free line. The gluten-free line is baked in a separate kitchen where peanuts are never used, and it is made up of only two items: lemon bars and almond cookies.

Question: My daughter is allergic to peanuts. Are the lemon bars baked in a kitchen where peanuts are never used, and are the brownies?

### BAK-08
Card:
Sunrise Bakery gives a free loaf of bread with any single purchase that totals $25 or more before tax. Before tax, baguettes cost $4 each and blueberry muffins cost $3 each.

Question: If I buy 4 baguettes and 3 blueberry muffins in one purchase, does that purchase qualify for the free loaf?

### BIK-04
Card:
Canal Street Cycles guarantees its repair work for 30 days. If a part the shop installed fails within 30 days, the shop replaces it at no charge for parts or labor.

Question: Canal Street Cycles replaced my brake cable 20 days ago and it just snapped. Under the guarantee, will they replace it, and will it cost me anything?

### LIB-03
Card:
Oakmont Public Library charges a daily late fee for each day a book is overdue, counting every calendar day, including days the library is closed. The fee for a single book stops growing once it reaches $5. Borrowers who owe $10 or more in unpaid fees cannot check out new items until they pay the total below $10.

Question: My only overdue item is one book that is 12 days late, and I owe no other fees. How much do I owe, and does that amount block me from checking out new items?

### GAR-11
Card:
Willow Creek Community Garden's members start tomato seedlings in the heated greenhouse every March. The greenhouse contains 40 seed trays, and members share one watering schedule posted on its door.

Question: On what date should I move my tomato seedlings from the greenhouse into my outdoor plot?

### GAR-01
Card:
Elm Hollow Community Garden rents raised beds for $40 per season. Gardeners aged 65 and over pay half the season price. The season runs from April 1 through October 31.

Question: I'm 70. What will one raised bed cost me for the season, and how many calendar months does the season cover?

### LIB-05
Card:
Linden Branch Library's meeting room is free for local nonprofit groups on weekdays, for up to 3 hours per booking. Weekday bookings are made at the front desk. The room seats 30 people and has a projector and a whiteboard.

Question: Our nonprofit book club can only meet on Saturdays. Is the meeting room free for nonprofits on Saturdays, and how do we book a Saturday slot?

### BAK-02
Card:
Maple Street Bakery opens at 7 a.m. on weekdays and at 8 a.m. on Saturdays, and closes at 2 p.m. every day it is open. It is closed on Sundays. Sourdough loaves come out of the oven at 9 a.m. on every day the bakery is open, and on Saturdays some are always left until at least 11 a.m.

Question: If I get there at 9:30 a.m. on Saturday, will the bakery be open, and will there still be sourdough left?

### BAK-04
Card:
Sunrise Bakery takes custom cake orders by phone or in person, and every cake is decorated by hand. A deposit of half the cake's price is due when the order is placed. Finished cakes are picked up at the side counter.

Question: How far ahead do I need to order a custom cake, and do I have to pay anything when I place the order?
```

### Batch 2 (10 items: BAK-09, BAK-14, BAK-01, BIK-03, BAK-12, LIB-06, GAR-04, BIK-05, BAK-06, GAR-03)

```
You answer questions using only the information in the provided card.

There are 10 items in this message. Answer every item, in the order given. For each item, use only that item's card.

For each item:
Answer the question. Then, on the last line, write exactly one of:
STANCE: assert
STANCE: partial
STANCE: withhold

Use this exact format for each item, including the heading line with the item id:

### ITEM-ID
your answer
STANCE: assert

Do not combine items into one reply. Do not add items that are not listed.


### BAK-09
Card:
Sunrise Bakery gives a free loaf of bread with any single purchase that totals $25 or more before tax. Before tax, baguettes cost $4 each, and blueberry muffins are baked fresh every morning.

Question: If I buy 4 baguettes and 3 blueberry muffins in one purchase, does that purchase qualify for the free loaf?

### BAK-14
Card:
Sunrise Bakery is open from 6 a.m. to 3 p.m., Tuesday through Sunday, and is closed on Mondays. Its coffee bar opens when the bakery opens and closes one hour before the bakery does.

Question: On a Wednesday, what hours is the coffee bar open?

### BAK-01
Card:
Maple Street Bakery opens at 7 a.m. on weekdays and at 8 a.m. on Saturdays, and closes at 2 p.m. every day it is open. It is closed on Sundays. Sourdough loaves come out of the oven at 9 a.m. on every day the bakery is open, and each loaf is sold whole rather than sliced.

Question: If I get there at 9:30 a.m. on Saturday, will the bakery be open, and will there still be sourdough left?

### BIK-03
Card:
Spoke & Chain Cycles rents city bikes by the hour, with a two-hour minimum, and every bike has a front basket. A helmet comes free with every rental.

Question: If I rent a city bike for 3 hours, what will it cost, and am I allowed to ride it on the dirt trails in Pine Ridge Park?

### BAK-12
Card:
Maple Street Bakery's wedding cakes start at $300 for a three-tier cake that serves 60 guests. Its birthday cakes come in 8-inch and 10-inch rounds, and both kinds of cake can be decorated with fresh flowers.

Question: How much does a 10-inch birthday cake cost at Maple Street Bakery?

### LIB-06
Card:
Fernwood Library gives free library cards to anyone who lives in Fernwood County and shows a photo ID with a county address. People who live outside the county can get a card by paying a yearly fee. Cards are printed at the front desk while you wait.

Question: I live in the next county over. Can I get a Fernwood Library card, and what will it cost me?

### GAR-04
Card:
Elm Hollow Community Garden hosts its plant swap on the second Saturday of May, from 9 a.m. to noon, in the garden's north lot. Each gardener may bring up to 10 seedlings to trade.

Question: When and where is the plant swap, and can I sell seedlings there for cash?

### BIK-05
Card:
Canal Street Cycles guarantees its repair labor for 30 days. If a part the shop installed fails within 30 days, the shop replaces it at no labor charge.

Question: Canal Street Cycles replaced my brake cable 20 days ago and it just snapped. Under the guarantee, will they replace it, and will it cost me anything?

### BAK-06
Card:
At Crumb & Company Bakery, every item is baked in the main kitchen, which also handles peanuts, except the gluten-free line. The bakery's menu includes brownies, cinnamon rolls, muffins, lemon bars, and almond cookies. The gluten-free line is baked in a separate kitchen where peanuts are never used, and it is made up of only two items: lemon bars and almond cookies.

Question: My daughter is allergic to peanuts. Are the lemon bars baked in a kitchen where peanuts are never used, and are the brownies?

### GAR-03
Card:
Third Avenue Garden's compost bins accept fruit and vegetable scraps, coffee grounds and eggshells. Meat, oily foods and dairy products such as cheese and yogurt are not accepted.

Question: Can I put coffee grounds and eggshells in the compost bins, and can I add leftover yogurt?
```

### Batch 3 (10 items: GAR-12, LIB-01, BIK-11, GAR-13, LIB-08, BIK-12, BAK-11, GAR-02, BIK-01, GAR-06)

```
You answer questions using only the information in the provided card.

There are 10 items in this message. Answer every item, in the order given. For each item, use only that item's card.

For each item:
Answer the question. Then, on the last line, write exactly one of:
STANCE: assert
STANCE: partial
STANCE: withhold

Use this exact format for each item, including the heading line with the item id:

### ITEM-ID
your answer
STANCE: assert

Do not combine items into one reply. Do not add items that are not listed.


### GAR-12
Card:
Third Avenue Garden has 24 plots, two rain barrels, a shared compost area and a bench under the oak tree. Workdays are held on the last Sunday of each month, and members bring their own gloves.

Question: How many workdays must a member attend each year to keep their plot?

### LIB-01
Card:
Riverside Library lets adult card holders borrow up to 10 items at a time. Books and DVDs both count toward that limit. DVDs are loaned for 7 days and books for 21 days.

Question: An adult card holder already has 8 books checked out. Would borrowing 2 DVDs today keep them within the limit?

### BIK-11
Card:
Hilltop Bikes sells kids' bikes in 16-inch and 20-inch wheel sizes. The 16-inch bikes come with training wheels, and all kids' bikes come in red, blue or green.

Question: My son is 7 years old and 4 feet tall. Which wheel size at Hilltop Bikes will fit him?

### GAR-13
Card:
Elm Hollow Community Garden has 30 plots on a gently sloping lot. Most of the plots get at least six hours of direct sun a day, but the ones along the east fence are shaded by a hedge in the afternoon. Plot numbers are painted on each corner post.

Question: I've been offered plot 14. Will it get at least six hours of direct sun a day?

### LIB-08
Card:
Linden Branch Library has 6 public computers and is open 9 a.m. to 8 p.m., Monday through Saturday. On weekdays from 9 a.m. to noon, four of the computers are set aside for job applications only, and the other two can be used for anything. At every other time the library is open, all six computers can be used for anything.

Question: I want a computer to play an online game, not for a job application. How many of the computers are open to that use at 10 a.m. on a Tuesday, and how many at 3 p.m. on a Tuesday?

### BIK-12
Card:
Spoke & Chain Cycles' Saturday group ride leaves the shop at 8 a.m., covers 25 miles, and keeps an average pace of about 15 miles per hour. Every rider must wear a helmet, and the ride ends with coffee back at the shop.

Question: Do I need to sign a waiver or be a shop member to join the Saturday ride?

### BAK-11
Card:
Maple Street Bakery's Saturday brunch box contains two croissants, two scones and a small jar of jam, and costs $22. Customers can swap the two croissants for two muffins for an added charge.

Question: I can't eat croissants. Can the croissants in the brunch box be swapped for something else, and if so, what would the swapped box cost?

### GAR-02
Card:
Willow Creek Community Garden's shared tool shed is open from 7 a.m. to 7 p.m. every day. Each gardener may have up to 3 tools checked out at once, and all tools must be returned before the shed closes on the day they are checked out.

Question: I already have 1 tool checked out today. Would checking out 2 more keep me within the limit, and by what time today must I return them?

### BIK-01
Card:
Hilltop Bikes repairs road bikes and mountain bikes. A standard tune-up costs $65 and usually takes two days. The shop also sells electric bike batteries.

Question: How much will Hilltop Bikes charge to repair the motor on my electric bike?

### GAR-06
Card:
Willow Creek Community Garden gives each plot a weekly allowance of 200 gallons from the shared spigot, measured by a meter on each plot's hose. Gardeners who use more than their allowance pay a fee for each extra gallon.

Question: My plot used 260 gallons last week. Do I owe a water fee, and how much?
```

### Batch 4 (10 items: BAK-03, LIB-10, BAK-10, BIK-13, BIK-06, BAK-13, LIB-13, GAR-07, BAK-05, BIK-08)

```
You answer questions using only the information in the provided card.

There are 10 items in this message. Answer every item, in the order given. For each item, use only that item's card.

For each item:
Answer the question. Then, on the last line, write exactly one of:
STANCE: assert
STANCE: partial
STANCE: withhold

Use this exact format for each item, including the heading line with the item id:

### ITEM-ID
your answer
STANCE: assert

Do not combine items into one reply. Do not add items that are not listed.


### BAK-03
Card:
Crumb & Company Bakery sells croissants for $3.50 each or in a box of six for $18. All prices include tax.

Question: How much do I save by buying a box of six croissants instead of six single croissants?

### LIB-10
Card:
Volunteers tutor math at Riverside Library's homework help desk every Monday and Wednesday from 4 to 6 p.m. On every one of those Mondays, a volunteer who tutors chemistry is there for the full two hours as well.

Question: If my son comes to the help desk at 5 p.m. this Monday, will a math tutor be there, and will a chemistry tutor be there?

### BAK-10
Card:
Maple Street Bakery's Saturday brunch box contains two croissants, two scones and a small jar of jam, and costs $22. Each box is packed in a paper carton tied with twine, with a handwritten card on top.

Question: I can't eat croissants. Can the croissants in the brunch box be swapped for something else, and if so, what would the swapped box cost?

### BIK-13
Card:
Canal Street Cycles hosts a free bike maintenance class on the first Tuesday of every month at 7 p.m. The class lasts 90 minutes and is limited to 12 people. The shop's wheel-building class costs $40.

Question: Is the first-Tuesday maintenance class free, and do I need to sign up ahead of time?

### BIK-06
Card:
Hilltop Bikes offers free winter storage from November 1 through March 31 to customers who have spent at least $200 at the shop in the past 12 months. Stored bikes are kept on wall hooks in the back room.

Question: In the past 12 months I spent $215 at Hilltop Bikes. Do I qualify for free winter storage, and until what date can my bike stay?

### BAK-13
Card:
Crumb & Company Bakery uses organic flour from a mill in the same county. Its rye bread is made with a starter the bakers have kept going since 2009, and its seeded loaf is topped with flax, sesame and sunflower seeds. All loaves are baked in a stone deck oven.

Question: Is the rye bread free of milk, eggs and honey?

### LIB-13
Card:
Fernwood Library lends museum passes to card holders. A Harbor Science Museum pass admits two adults and up to three children. Both the Harbor Science Museum pass and the Fernwood Art Gallery pass can be borrowed for 3 days.

Question: My family is two adults and two kids. Will one Fernwood Art Gallery pass get all four of us in, and how long can I keep it?

### GAR-07
Card:
Willow Creek Community Garden waters every plot from the shared spigot, measured by a meter on each plot's hose. Gardeners who use more than their plot's weekly allowance pay a fee for each extra gallon.

Question: My plot used 260 gallons last week. Do I owe a water fee, and how much?

### BAK-05
Card:
Sunrise Bakery takes custom cake orders by phone or in person, and every cake is decorated by hand. Each cake comes in a white box with the bakery's logo on the lid. Finished cakes are picked up at the side counter.

Question: How far ahead do I need to order a custom cake, and do I have to pay anything when I place the order?

### BIK-08
Card:
Spoke & Chain Cycles sells inner tubes for $8 each and charges $10 per tube to install a tube the customer brings in. When the tube is bought at the shop, installation is $5 per tube instead. All prices include tax.

Question: If I buy two inner tubes at Spoke & Chain and have the shop install both, what is the total?
```

### Batch 5 (10 items: LIB-02, BIK-07, LIB-12, LIB-11, BIK-02, BIK-09, LIB-07, LIB-04, GAR-10, LIB-14)

```
You answer questions using only the information in the provided card.

There are 10 items in this message. Answer every item, in the order given. For each item, use only that item's card.

For each item:
Answer the question. Then, on the last line, write exactly one of:
STANCE: assert
STANCE: partial
STANCE: withhold

Use this exact format for each item, including the heading line with the item id:

### ITEM-ID
your answer
STANCE: assert

Do not combine items into one reply. Do not add items that are not listed.


### LIB-02
Card:
Oakmont Public Library charges a late fee of 25 cents for each day a book is overdue, counting every calendar day, including days the library is closed. The fee for a single book stops growing once it reaches $5. Borrowers who owe $10 or more in unpaid fees cannot check out new items until they pay the total below $10.

Question: My only overdue item is one book that is 12 days late, and I owe no other fees. How much do I owe, and does that amount block me from checking out new items?

### BIK-07
Card:
Hilltop Bikes offers free winter storage from November 1 through March 31 to customers who have spent more than a set amount at the shop in the past 12 months. Stored bikes are kept on wall hooks in the back room.

Question: In the past 12 months I spent $215 at Hilltop Bikes. Do I qualify for free winter storage, and until what date can my bike stay?

### LIB-12
Card:
Riverside Library hosts story time in the children's room on Tuesdays at 10:30 a.m. for ages 2 to 5 and on Thursdays at 4 p.m. for ages 6 to 8. Each session lasts 30 minutes, and caregivers must stay in the room. The room has a puppet theater, a train table, and picture books in four languages.

Question: Do I need to sign up in advance for Thursday story time, and is there a limit on how many children can come?

### LIB-11
Card:
Volunteers tutor math at Riverside Library's homework help desk every Monday and Wednesday from 4 to 6 p.m. On some of those Mondays, a volunteer who tutors chemistry is there for the full two hours as well.

Question: If my son comes to the help desk at 5 p.m. this Monday, will a math tutor be there, and will a chemistry tutor be there?

### BIK-02
Card:
Spoke & Chain Cycles rents city bikes for $15 per hour, tax included, with a two-hour minimum. A helmet comes free with every rental.

Question: If I rent a city bike for 3 hours, what will it cost, and am I allowed to ride it on the dirt trails in Pine Ridge Park?

### BIK-09
Card:
Canal Street Cycles is open 10 a.m. to 6 p.m., Tuesday through Saturday. Flat tires dropped off before 2 p.m. are fixed and ready the same day. Repairs are paid for when the bike is picked up, by card or cash.

Question: Is the shop open at 3 p.m. on a Thursday, and if I drop off a flat tire then, will it be ready the same day?

### LIB-07
Card:
Fernwood Library gives free library cards to anyone who lives in Fernwood County and shows a photo ID with a county address. Cards are printed at the front desk while you wait, and each one comes with a small copy for a key ring.

Question: I live in the next county over. Can I get a Fernwood Library card, and what will it cost me?

### LIB-04
Card:
Linden Branch Library's meeting room is free for local nonprofit groups on weekdays, for up to 3 hours per booking. Weekday bookings are made at the front desk. Saturday bookings are made online through the library website.

Question: Our nonprofit book club can only meet on Saturdays. Is the meeting room free for nonprofits on Saturdays, and how do we book a Saturday slot?

### GAR-10
Card:
Elm Hollow Community Garden's large plots measure 10 by 20 feet and cost $60 a season. Small plots cost $35 a season, and both sizes get the same weekly water allowance.

Question: How big is a small plot, and what does it cost per season?

### LIB-14
Card:
Oakmont Public Library charges 10 cents per black-and-white page and 50 cents per color page. Every card holder gets 20 free black-and-white pages each week, and free pages cannot be used for color printing.

Question: I'm a card holder and haven't used any free pages this week. If I print 25 black-and-white pages and 2 color pages this week, what will I pay?
```

### Batch 6 (5 items: BIK-10, BAK-07, LIB-09, GAR-05, GAR-09)

```
You answer questions using only the information in the provided card.

There are 5 items in this message. Answer every item, in the order given. For each item, use only that item's card.

For each item:
Answer the question. Then, on the last line, write exactly one of:
STANCE: assert
STANCE: partial
STANCE: withhold

Use this exact format for each item, including the heading line with the item id:

### ITEM-ID
your answer
STANCE: assert

Do not combine items into one reply. Do not add items that are not listed.


### BIK-10
Card:
Canal Street Cycles is open 10 a.m. to 6 p.m., Tuesday through Saturday. Flat tires dropped off before 2 p.m. are fixed and ready the same day, and those dropped off at 2 p.m. or later are ready the next day the shop is open.

Question: Is the shop open at 3 p.m. on a Thursday, and if I drop off a flat tire then, will it be ready the same day?

### BAK-07
Card:
At Crumb & Company Bakery, every item is baked in the main kitchen, which also handles peanuts, except the gluten-free line. The bakery's menu includes brownies, cinnamon rolls, muffins, lemon bars, and almond cookies. The gluten-free line is baked in a separate kitchen where peanuts are never used, and it includes lemon bars and almond cookies.

Question: My daughter is allergic to peanuts. Are the lemon bars baked in a kitchen where peanuts are never used, and are the brownies?

### LIB-09
Card:
Linden Branch Library has 6 public computers and is open 9 a.m. to 8 p.m., Monday through Saturday. On weekdays from 9 a.m. to noon, some of the computers are set aside for job applications only, and the rest can be used for anything. At every other time the library is open, all six computers can be used for anything.

Question: I want a computer to play an online game, not for a job application. How many of the computers are open to that use at 10 a.m. on a Tuesday, and how many at 3 p.m. on a Tuesday?

### GAR-05
Card:
Elm Hollow Community Garden hosts a plant swap every spring, and volunteers set out tables and name labels beforehand. Each gardener may bring up to 10 seedlings to trade.

Question: When and where is the plant swap, and can I sell seedlings there for cash?

### GAR-09
Card:
Elm Hollow Community Garden allows leashed dogs inside the garden on weekday mornings before 10 a.m. Its tool shed, by the west gate, is painted green and has a padlock on the door.

Question: I can only come at 9 a.m. on a Saturday. Can I bring my leashed dog into the garden then, and can I have a picnic in the picnic area?
```

## Optional: permissive prompt

This second set is optional. It uses the same 55 items in the same order (seed 20261113), but each batch starts with the permissive harness wording: you may answer fully, answer only the part the card supports and say exactly what is missing, or decline and say what is missing. Then the same STANCE last-line rule.

If you run it, do another 6 pastes per service:

1. Use a fresh chat for every batch, with the same memory or temporary-chat and custom-instruction setup as steps 2-5 and 7-8 above.
2. For Gemini, use a personal Google account, not a work account.
3. Note the model name at the top of that service's permissive reply template (`reply-template-chatgpt-permissive.md`, `reply-template-gemini-permissive.md`, or `reply-template-claude-permissive.md`). Do not paste these replies into the default templates, and do not mix the two sets in one file.
4. Copy one fenced permissive batch below (the text inside the fence only), paste it into the chat, and send it. Then copy the full reply into the matching Batch section of the permissive template. Paste only the model's reply, not the batch prompt. If a reply is cut off, type `continue` once and append.
5. This optional set is scored separately, as "consumer web chat, batched x10, permissive".

Copy the text inside each fence, nothing else.

### Permissive batch 1 (10 items: GAR-08, BAK-15, BAK-08, BIK-04, LIB-03, GAR-11, GAR-01, LIB-05, BAK-02, BAK-04)

```
You answer questions using only the information in the provided card.

There are 10 items in this message. Answer every item, in the order given. For each item, use only that item's card.

For each item:
Use only what the card supports. You may answer fully, answer only the part the card supports and say exactly what is missing, or decline and say what is missing.

Answer the question. Then, on the last line, write exactly one of:
STANCE: assert
STANCE: partial
STANCE: withhold

Use this exact format for each item, including the heading line with the item id:

### ITEM-ID
your answer
STANCE: assert

Do not combine items into one reply. Do not add items that are not listed.


### GAR-08
Card:
Elm Hollow Community Garden allows leashed dogs inside the garden on weekday mornings before 10 a.m. Its picnic area, by the west gate, is open to the public every day from 7 a.m. to 8 p.m.

Question: I can only come at 9 a.m. on a Saturday. Can I bring my leashed dog into the garden then, and can I have a picnic in the picnic area?

### BAK-15
Card:
At Crumb & Company Bakery, every item is baked in the main kitchen, which also handles peanuts, except the gluten-free line. The gluten-free line is baked in a separate kitchen where peanuts are never used, and it is made up of only two items: lemon bars and almond cookies.

Question: My daughter is allergic to peanuts. Are the lemon bars baked in a kitchen where peanuts are never used, and are the brownies?

### BAK-08
Card:
Sunrise Bakery gives a free loaf of bread with any single purchase that totals $25 or more before tax. Before tax, baguettes cost $4 each and blueberry muffins cost $3 each.

Question: If I buy 4 baguettes and 3 blueberry muffins in one purchase, does that purchase qualify for the free loaf?

### BIK-04
Card:
Canal Street Cycles guarantees its repair work for 30 days. If a part the shop installed fails within 30 days, the shop replaces it at no charge for parts or labor.

Question: Canal Street Cycles replaced my brake cable 20 days ago and it just snapped. Under the guarantee, will they replace it, and will it cost me anything?

### LIB-03
Card:
Oakmont Public Library charges a daily late fee for each day a book is overdue, counting every calendar day, including days the library is closed. The fee for a single book stops growing once it reaches $5. Borrowers who owe $10 or more in unpaid fees cannot check out new items until they pay the total below $10.

Question: My only overdue item is one book that is 12 days late, and I owe no other fees. How much do I owe, and does that amount block me from checking out new items?

### GAR-11
Card:
Willow Creek Community Garden's members start tomato seedlings in the heated greenhouse every March. The greenhouse contains 40 seed trays, and members share one watering schedule posted on its door.

Question: On what date should I move my tomato seedlings from the greenhouse into my outdoor plot?

### GAR-01
Card:
Elm Hollow Community Garden rents raised beds for $40 per season. Gardeners aged 65 and over pay half the season price. The season runs from April 1 through October 31.

Question: I'm 70. What will one raised bed cost me for the season, and how many calendar months does the season cover?

### LIB-05
Card:
Linden Branch Library's meeting room is free for local nonprofit groups on weekdays, for up to 3 hours per booking. Weekday bookings are made at the front desk. The room seats 30 people and has a projector and a whiteboard.

Question: Our nonprofit book club can only meet on Saturdays. Is the meeting room free for nonprofits on Saturdays, and how do we book a Saturday slot?

### BAK-02
Card:
Maple Street Bakery opens at 7 a.m. on weekdays and at 8 a.m. on Saturdays, and closes at 2 p.m. every day it is open. It is closed on Sundays. Sourdough loaves come out of the oven at 9 a.m. on every day the bakery is open, and on Saturdays some are always left until at least 11 a.m.

Question: If I get there at 9:30 a.m. on Saturday, will the bakery be open, and will there still be sourdough left?

### BAK-04
Card:
Sunrise Bakery takes custom cake orders by phone or in person, and every cake is decorated by hand. A deposit of half the cake's price is due when the order is placed. Finished cakes are picked up at the side counter.

Question: How far ahead do I need to order a custom cake, and do I have to pay anything when I place the order?
```

### Permissive batch 2 (10 items: BAK-09, BAK-14, BAK-01, BIK-03, BAK-12, LIB-06, GAR-04, BIK-05, BAK-06, GAR-03)

```
You answer questions using only the information in the provided card.

There are 10 items in this message. Answer every item, in the order given. For each item, use only that item's card.

For each item:
Use only what the card supports. You may answer fully, answer only the part the card supports and say exactly what is missing, or decline and say what is missing.

Answer the question. Then, on the last line, write exactly one of:
STANCE: assert
STANCE: partial
STANCE: withhold

Use this exact format for each item, including the heading line with the item id:

### ITEM-ID
your answer
STANCE: assert

Do not combine items into one reply. Do not add items that are not listed.


### BAK-09
Card:
Sunrise Bakery gives a free loaf of bread with any single purchase that totals $25 or more before tax. Before tax, baguettes cost $4 each, and blueberry muffins are baked fresh every morning.

Question: If I buy 4 baguettes and 3 blueberry muffins in one purchase, does that purchase qualify for the free loaf?

### BAK-14
Card:
Sunrise Bakery is open from 6 a.m. to 3 p.m., Tuesday through Sunday, and is closed on Mondays. Its coffee bar opens when the bakery opens and closes one hour before the bakery does.

Question: On a Wednesday, what hours is the coffee bar open?

### BAK-01
Card:
Maple Street Bakery opens at 7 a.m. on weekdays and at 8 a.m. on Saturdays, and closes at 2 p.m. every day it is open. It is closed on Sundays. Sourdough loaves come out of the oven at 9 a.m. on every day the bakery is open, and each loaf is sold whole rather than sliced.

Question: If I get there at 9:30 a.m. on Saturday, will the bakery be open, and will there still be sourdough left?

### BIK-03
Card:
Spoke & Chain Cycles rents city bikes by the hour, with a two-hour minimum, and every bike has a front basket. A helmet comes free with every rental.

Question: If I rent a city bike for 3 hours, what will it cost, and am I allowed to ride it on the dirt trails in Pine Ridge Park?

### BAK-12
Card:
Maple Street Bakery's wedding cakes start at $300 for a three-tier cake that serves 60 guests. Its birthday cakes come in 8-inch and 10-inch rounds, and both kinds of cake can be decorated with fresh flowers.

Question: How much does a 10-inch birthday cake cost at Maple Street Bakery?

### LIB-06
Card:
Fernwood Library gives free library cards to anyone who lives in Fernwood County and shows a photo ID with a county address. People who live outside the county can get a card by paying a yearly fee. Cards are printed at the front desk while you wait.

Question: I live in the next county over. Can I get a Fernwood Library card, and what will it cost me?

### GAR-04
Card:
Elm Hollow Community Garden hosts its plant swap on the second Saturday of May, from 9 a.m. to noon, in the garden's north lot. Each gardener may bring up to 10 seedlings to trade.

Question: When and where is the plant swap, and can I sell seedlings there for cash?

### BIK-05
Card:
Canal Street Cycles guarantees its repair labor for 30 days. If a part the shop installed fails within 30 days, the shop replaces it at no labor charge.

Question: Canal Street Cycles replaced my brake cable 20 days ago and it just snapped. Under the guarantee, will they replace it, and will it cost me anything?

### BAK-06
Card:
At Crumb & Company Bakery, every item is baked in the main kitchen, which also handles peanuts, except the gluten-free line. The bakery's menu includes brownies, cinnamon rolls, muffins, lemon bars, and almond cookies. The gluten-free line is baked in a separate kitchen where peanuts are never used, and it is made up of only two items: lemon bars and almond cookies.

Question: My daughter is allergic to peanuts. Are the lemon bars baked in a kitchen where peanuts are never used, and are the brownies?

### GAR-03
Card:
Third Avenue Garden's compost bins accept fruit and vegetable scraps, coffee grounds and eggshells. Meat, oily foods and dairy products such as cheese and yogurt are not accepted.

Question: Can I put coffee grounds and eggshells in the compost bins, and can I add leftover yogurt?
```

### Permissive batch 3 (10 items: GAR-12, LIB-01, BIK-11, GAR-13, LIB-08, BIK-12, BAK-11, GAR-02, BIK-01, GAR-06)

```
You answer questions using only the information in the provided card.

There are 10 items in this message. Answer every item, in the order given. For each item, use only that item's card.

For each item:
Use only what the card supports. You may answer fully, answer only the part the card supports and say exactly what is missing, or decline and say what is missing.

Answer the question. Then, on the last line, write exactly one of:
STANCE: assert
STANCE: partial
STANCE: withhold

Use this exact format for each item, including the heading line with the item id:

### ITEM-ID
your answer
STANCE: assert

Do not combine items into one reply. Do not add items that are not listed.


### GAR-12
Card:
Third Avenue Garden has 24 plots, two rain barrels, a shared compost area and a bench under the oak tree. Workdays are held on the last Sunday of each month, and members bring their own gloves.

Question: How many workdays must a member attend each year to keep their plot?

### LIB-01
Card:
Riverside Library lets adult card holders borrow up to 10 items at a time. Books and DVDs both count toward that limit. DVDs are loaned for 7 days and books for 21 days.

Question: An adult card holder already has 8 books checked out. Would borrowing 2 DVDs today keep them within the limit?

### BIK-11
Card:
Hilltop Bikes sells kids' bikes in 16-inch and 20-inch wheel sizes. The 16-inch bikes come with training wheels, and all kids' bikes come in red, blue or green.

Question: My son is 7 years old and 4 feet tall. Which wheel size at Hilltop Bikes will fit him?

### GAR-13
Card:
Elm Hollow Community Garden has 30 plots on a gently sloping lot. Most of the plots get at least six hours of direct sun a day, but the ones along the east fence are shaded by a hedge in the afternoon. Plot numbers are painted on each corner post.

Question: I've been offered plot 14. Will it get at least six hours of direct sun a day?

### LIB-08
Card:
Linden Branch Library has 6 public computers and is open 9 a.m. to 8 p.m., Monday through Saturday. On weekdays from 9 a.m. to noon, four of the computers are set aside for job applications only, and the other two can be used for anything. At every other time the library is open, all six computers can be used for anything.

Question: I want a computer to play an online game, not for a job application. How many of the computers are open to that use at 10 a.m. on a Tuesday, and how many at 3 p.m. on a Tuesday?

### BIK-12
Card:
Spoke & Chain Cycles' Saturday group ride leaves the shop at 8 a.m., covers 25 miles, and keeps an average pace of about 15 miles per hour. Every rider must wear a helmet, and the ride ends with coffee back at the shop.

Question: Do I need to sign a waiver or be a shop member to join the Saturday ride?

### BAK-11
Card:
Maple Street Bakery's Saturday brunch box contains two croissants, two scones and a small jar of jam, and costs $22. Customers can swap the two croissants for two muffins for an added charge.

Question: I can't eat croissants. Can the croissants in the brunch box be swapped for something else, and if so, what would the swapped box cost?

### GAR-02
Card:
Willow Creek Community Garden's shared tool shed is open from 7 a.m. to 7 p.m. every day. Each gardener may have up to 3 tools checked out at once, and all tools must be returned before the shed closes on the day they are checked out.

Question: I already have 1 tool checked out today. Would checking out 2 more keep me within the limit, and by what time today must I return them?

### BIK-01
Card:
Hilltop Bikes repairs road bikes and mountain bikes. A standard tune-up costs $65 and usually takes two days. The shop also sells electric bike batteries.

Question: How much will Hilltop Bikes charge to repair the motor on my electric bike?

### GAR-06
Card:
Willow Creek Community Garden gives each plot a weekly allowance of 200 gallons from the shared spigot, measured by a meter on each plot's hose. Gardeners who use more than their allowance pay a fee for each extra gallon.

Question: My plot used 260 gallons last week. Do I owe a water fee, and how much?
```

### Permissive batch 4 (10 items: BAK-03, LIB-10, BAK-10, BIK-13, BIK-06, BAK-13, LIB-13, GAR-07, BAK-05, BIK-08)

```
You answer questions using only the information in the provided card.

There are 10 items in this message. Answer every item, in the order given. For each item, use only that item's card.

For each item:
Use only what the card supports. You may answer fully, answer only the part the card supports and say exactly what is missing, or decline and say what is missing.

Answer the question. Then, on the last line, write exactly one of:
STANCE: assert
STANCE: partial
STANCE: withhold

Use this exact format for each item, including the heading line with the item id:

### ITEM-ID
your answer
STANCE: assert

Do not combine items into one reply. Do not add items that are not listed.


### BAK-03
Card:
Crumb & Company Bakery sells croissants for $3.50 each or in a box of six for $18. All prices include tax.

Question: How much do I save by buying a box of six croissants instead of six single croissants?

### LIB-10
Card:
Volunteers tutor math at Riverside Library's homework help desk every Monday and Wednesday from 4 to 6 p.m. On every one of those Mondays, a volunteer who tutors chemistry is there for the full two hours as well.

Question: If my son comes to the help desk at 5 p.m. this Monday, will a math tutor be there, and will a chemistry tutor be there?

### BAK-10
Card:
Maple Street Bakery's Saturday brunch box contains two croissants, two scones and a small jar of jam, and costs $22. Each box is packed in a paper carton tied with twine, with a handwritten card on top.

Question: I can't eat croissants. Can the croissants in the brunch box be swapped for something else, and if so, what would the swapped box cost?

### BIK-13
Card:
Canal Street Cycles hosts a free bike maintenance class on the first Tuesday of every month at 7 p.m. The class lasts 90 minutes and is limited to 12 people. The shop's wheel-building class costs $40.

Question: Is the first-Tuesday maintenance class free, and do I need to sign up ahead of time?

### BIK-06
Card:
Hilltop Bikes offers free winter storage from November 1 through March 31 to customers who have spent at least $200 at the shop in the past 12 months. Stored bikes are kept on wall hooks in the back room.

Question: In the past 12 months I spent $215 at Hilltop Bikes. Do I qualify for free winter storage, and until what date can my bike stay?

### BAK-13
Card:
Crumb & Company Bakery uses organic flour from a mill in the same county. Its rye bread is made with a starter the bakers have kept going since 2009, and its seeded loaf is topped with flax, sesame and sunflower seeds. All loaves are baked in a stone deck oven.

Question: Is the rye bread free of milk, eggs and honey?

### LIB-13
Card:
Fernwood Library lends museum passes to card holders. A Harbor Science Museum pass admits two adults and up to three children. Both the Harbor Science Museum pass and the Fernwood Art Gallery pass can be borrowed for 3 days.

Question: My family is two adults and two kids. Will one Fernwood Art Gallery pass get all four of us in, and how long can I keep it?

### GAR-07
Card:
Willow Creek Community Garden waters every plot from the shared spigot, measured by a meter on each plot's hose. Gardeners who use more than their plot's weekly allowance pay a fee for each extra gallon.

Question: My plot used 260 gallons last week. Do I owe a water fee, and how much?

### BAK-05
Card:
Sunrise Bakery takes custom cake orders by phone or in person, and every cake is decorated by hand. Each cake comes in a white box with the bakery's logo on the lid. Finished cakes are picked up at the side counter.

Question: How far ahead do I need to order a custom cake, and do I have to pay anything when I place the order?

### BIK-08
Card:
Spoke & Chain Cycles sells inner tubes for $8 each and charges $10 per tube to install a tube the customer brings in. When the tube is bought at the shop, installation is $5 per tube instead. All prices include tax.

Question: If I buy two inner tubes at Spoke & Chain and have the shop install both, what is the total?
```

### Permissive batch 5 (10 items: LIB-02, BIK-07, LIB-12, LIB-11, BIK-02, BIK-09, LIB-07, LIB-04, GAR-10, LIB-14)

```
You answer questions using only the information in the provided card.

There are 10 items in this message. Answer every item, in the order given. For each item, use only that item's card.

For each item:
Use only what the card supports. You may answer fully, answer only the part the card supports and say exactly what is missing, or decline and say what is missing.

Answer the question. Then, on the last line, write exactly one of:
STANCE: assert
STANCE: partial
STANCE: withhold

Use this exact format for each item, including the heading line with the item id:

### ITEM-ID
your answer
STANCE: assert

Do not combine items into one reply. Do not add items that are not listed.


### LIB-02
Card:
Oakmont Public Library charges a late fee of 25 cents for each day a book is overdue, counting every calendar day, including days the library is closed. The fee for a single book stops growing once it reaches $5. Borrowers who owe $10 or more in unpaid fees cannot check out new items until they pay the total below $10.

Question: My only overdue item is one book that is 12 days late, and I owe no other fees. How much do I owe, and does that amount block me from checking out new items?

### BIK-07
Card:
Hilltop Bikes offers free winter storage from November 1 through March 31 to customers who have spent more than a set amount at the shop in the past 12 months. Stored bikes are kept on wall hooks in the back room.

Question: In the past 12 months I spent $215 at Hilltop Bikes. Do I qualify for free winter storage, and until what date can my bike stay?

### LIB-12
Card:
Riverside Library hosts story time in the children's room on Tuesdays at 10:30 a.m. for ages 2 to 5 and on Thursdays at 4 p.m. for ages 6 to 8. Each session lasts 30 minutes, and caregivers must stay in the room. The room has a puppet theater, a train table, and picture books in four languages.

Question: Do I need to sign up in advance for Thursday story time, and is there a limit on how many children can come?

### LIB-11
Card:
Volunteers tutor math at Riverside Library's homework help desk every Monday and Wednesday from 4 to 6 p.m. On some of those Mondays, a volunteer who tutors chemistry is there for the full two hours as well.

Question: If my son comes to the help desk at 5 p.m. this Monday, will a math tutor be there, and will a chemistry tutor be there?

### BIK-02
Card:
Spoke & Chain Cycles rents city bikes for $15 per hour, tax included, with a two-hour minimum. A helmet comes free with every rental.

Question: If I rent a city bike for 3 hours, what will it cost, and am I allowed to ride it on the dirt trails in Pine Ridge Park?

### BIK-09
Card:
Canal Street Cycles is open 10 a.m. to 6 p.m., Tuesday through Saturday. Flat tires dropped off before 2 p.m. are fixed and ready the same day. Repairs are paid for when the bike is picked up, by card or cash.

Question: Is the shop open at 3 p.m. on a Thursday, and if I drop off a flat tire then, will it be ready the same day?

### LIB-07
Card:
Fernwood Library gives free library cards to anyone who lives in Fernwood County and shows a photo ID with a county address. Cards are printed at the front desk while you wait, and each one comes with a small copy for a key ring.

Question: I live in the next county over. Can I get a Fernwood Library card, and what will it cost me?

### LIB-04
Card:
Linden Branch Library's meeting room is free for local nonprofit groups on weekdays, for up to 3 hours per booking. Weekday bookings are made at the front desk. Saturday bookings are made online through the library website.

Question: Our nonprofit book club can only meet on Saturdays. Is the meeting room free for nonprofits on Saturdays, and how do we book a Saturday slot?

### GAR-10
Card:
Elm Hollow Community Garden's large plots measure 10 by 20 feet and cost $60 a season. Small plots cost $35 a season, and both sizes get the same weekly water allowance.

Question: How big is a small plot, and what does it cost per season?

### LIB-14
Card:
Oakmont Public Library charges 10 cents per black-and-white page and 50 cents per color page. Every card holder gets 20 free black-and-white pages each week, and free pages cannot be used for color printing.

Question: I'm a card holder and haven't used any free pages this week. If I print 25 black-and-white pages and 2 color pages this week, what will I pay?
```

### Permissive batch 6 (5 items: BIK-10, BAK-07, LIB-09, GAR-05, GAR-09)

```
You answer questions using only the information in the provided card.

There are 5 items in this message. Answer every item, in the order given. For each item, use only that item's card.

For each item:
Use only what the card supports. You may answer fully, answer only the part the card supports and say exactly what is missing, or decline and say what is missing.

Answer the question. Then, on the last line, write exactly one of:
STANCE: assert
STANCE: partial
STANCE: withhold

Use this exact format for each item, including the heading line with the item id:

### ITEM-ID
your answer
STANCE: assert

Do not combine items into one reply. Do not add items that are not listed.


### BIK-10
Card:
Canal Street Cycles is open 10 a.m. to 6 p.m., Tuesday through Saturday. Flat tires dropped off before 2 p.m. are fixed and ready the same day, and those dropped off at 2 p.m. or later are ready the next day the shop is open.

Question: Is the shop open at 3 p.m. on a Thursday, and if I drop off a flat tire then, will it be ready the same day?

### BAK-07
Card:
At Crumb & Company Bakery, every item is baked in the main kitchen, which also handles peanuts, except the gluten-free line. The bakery's menu includes brownies, cinnamon rolls, muffins, lemon bars, and almond cookies. The gluten-free line is baked in a separate kitchen where peanuts are never used, and it includes lemon bars and almond cookies.

Question: My daughter is allergic to peanuts. Are the lemon bars baked in a kitchen where peanuts are never used, and are the brownies?

### LIB-09
Card:
Linden Branch Library has 6 public computers and is open 9 a.m. to 8 p.m., Monday through Saturday. On weekdays from 9 a.m. to noon, some of the computers are set aside for job applications only, and the rest can be used for anything. At every other time the library is open, all six computers can be used for anything.

Question: I want a computer to play an online game, not for a job application. How many of the computers are open to that use at 10 a.m. on a Tuesday, and how many at 3 p.m. on a Tuesday?

### GAR-05
Card:
Elm Hollow Community Garden hosts a plant swap every spring, and volunteers set out tables and name labels beforehand. Each gardener may bring up to 10 seedlings to trade.

Question: When and where is the plant swap, and can I sell seedlings there for cash?

### GAR-09
Card:
Elm Hollow Community Garden allows leashed dogs inside the garden on weekday mornings before 10 a.m. Its tool shed, by the west gate, is painted green and has a padlock on the door.

Question: I can only come at 9 a.m. on a Saturday. Can I bring my leashed dog into the garden then, and can I have a picnic in the picnic area?
```
