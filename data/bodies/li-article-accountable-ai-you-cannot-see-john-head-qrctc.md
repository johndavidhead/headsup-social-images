# Accountable for AI you cannot see

2026-08-03 | https://www.linkedin.com/pulse/accountable-ai-you-cannot-see-john-head-qrctc/

Fact: 66% of CIOs and CTOs are held accountable for AI systems they do not fully control. [1]

That number is from IBM's 2026 Tech Leader Study, published in June. IBM surveyed 2,000 C-level technology executives across 33 geographies and 19 industries between January and April of this year. I read a lot of these studies and most of them tell me what I already hear in client meetings. This one landed differently. It says the AI problem in large enterprises has quietly stopped being a technology problem and turned into an accountability and budgeting problem. The rest of the study explains how it got that way, and it points at a first move that is smaller than most people expect.

The people deploying AI and the people answering for it are no longer the same people

70% of the executives surveyed say business teams deploy technology faster than IT can track it. [1] That is the mechanic behind the 66%. AI capability arrived inside software the business had already bought. Every major SaaS vendor shipped agents and assistants into products that marketing, finance, HR, and operations own outright. Nobody filed a project request. Nobody stood up a steering committee. The features turned on.

Deepika Giri at IDC described it as adoption happening at the edges of the organization while accountability stays at the top. [3] That matches what I see in the field. The CIO did not lose control through a failure of leadership. Control moved because the purchasing decision moved, and the org chart has not caught up to it.

11% readiness against 1,661 agents

Only 11% of these executives say they are fully prepared for the scale of AI agent deployment they expect. [1] The scale they expect is an average of 1,661 agents per enterprise by 2027, a 38% increase from where things stand now. [3] Meanwhile 80% are operating under a CEO mandate to move faster on AI. [1]

Those three numbers sit badly together. The board wants speed. The forecast is more than sixteen hundred autonomous or semi-autonomous processes per company inside eighteen months. Nine out of ten technology leaders say they are not ready for it.

I do not read the 11% as a confidence problem. Readiness at that volume means identity management for non-human actors, spend controls per agent, logging that survives an audit, and a rollback path for when an agent does something expensive at 2am. Most enterprises did not have all of that for their human users. Building it for agents, at that count, in eighteen months, is a real program with a real budget attached.

Governance is running behind, and further behind than most leaders admit

77% of the executives say AI adoption has already outrun their governance capability, and 59% name security and compliance as the biggest barrier to scaling further. [1] Together those describe a policy layer that is both late and blocking, which is the worst combination to be in.

The number I keep quoting back is IDC's: 16% of organizations have a unified AI governance model. [3] So when a CIO tells me they have AI governance in place, the honest follow-up question is which AI. Governance almost always covers the models IT deployed. It rarely covers the copilot embedded in the CRM, the summarizer in the ticketing tool, or the agent a business analyst configured last month inside a platform IT does not administer.

Governance that only sees IT-deployed models is a control reporting on the smallest slice of the exposure. That is why the 77% does not surprise me. Governance did not get worse. The surface area grew faster than the review process could scale, and it grew in places the review process was never pointed at.

Nobody has a meter on the AI bill

This is the part of the study I would put in front of a board.

AI goes from 15% of IT budgets in 2025 to 25% by 2027. Inside two years, a quarter of technology spend is AI. Against that, 84% of these organizations have not operationalized AI financial management and 85% have no real-time view of what AI is costing them right now. [1]

A quarter of the IT budget with no meter on it.

I have sat in enough renewal conversations to know how that ends. The bill arrives as a surprise in the middle of a fiscal year, someone freezes AI spend across the board, and the two use cases that were actually returning value get frozen alongside the forty that were not. The freeze is the real damage. It costs a year of momentum and it teaches the business that going through IT means getting shut down.

The study shows the other side of it too. Organizations with financial discipline around AI deploy 2.4x more agents and are 3x more likely to say they are prepared for what is coming. [1] That correlation is the useful part. Spend visibility and operational readiness turn out to be the same capability wearing two different labels. If you can see the cost of every agent, you already know what is running, who turned it on, and what it connects to. The invoice is often the fastest inventory tool a CIO has.

The reflex to clamp down is the expensive one

When leaders see these numbers, the first instinct is usually to centralize. Freeze new AI purchases. Route everything through architecture review. Put a committee in front of it.

I have watched that play out in client environments and it does not hold. The business units keep buying, they just stop telling IT. Shadow AI does not disappear under a stricter policy. It gets quieter, which is worse, because the exposure stays and the visibility drops.

Chris Pesola at Roush framed the alternative well in the study: create visibility and partnership so teams can get help when they need it without slowing down. [2] Sanchit Vir Gogia at Greyhound Research gave the diagnosis that stuck with me, that enterprises decentralized experimentation far faster than they decentralized accountability. [3] Experimentation will not come back to the center. Accountability has to go out and meet it.

In practice that means every AI capability running in the business has a named owner inside the business, a monthly cost, and a reporting line into one view that IT maintains. IT stops being the gate and becomes the meter and the map. That is a smaller role in one sense and a far more useful one in every other sense.

Where I would start in the next 30 days

Not with a governance program. Governance programs take a quarter to design and another quarter to socialize, and the gap keeps widening while you do it.

Start with an inventory. Every AI agent, copilot, and AI-enabled SaaS feature running in the business today, including the ones IT did not deploy. Pull it from your SSO logs and your procurement and expense data, then confirm it in a direct conversation with each business unit leader. Put a monthly cost against every line. Put a named business owner against every line.

That inventory is usually uncomfortable and always useful. It turns the governance conversation from a policy debate into a list you can work. It gives finance the number they are going to ask you for anyway. And it tells you honestly whether you are in the 11% or the 89%.

The question I would put to your leadership team

If you had to produce that list tomorrow, with an owner and a monthly cost next to every AI agent running in your business, how close could you get? And who is the first person you would have to call to fill in the gaps?

I would rather compare notes on this over coffee than in a comment thread. If you are working through it right now, let me know.

#EnterpriseAI  #AIGovernance  #AgenticAI  #CIO  #AIStrategy

References

[1] New IBM study finds CIOs and CTOs face growing AI control gap as enterprise deployment scales IBM Newsroom, June 8, 2026. Survey of 2,000 C-level technology executives across 33 geographies and 19 industries, fielded January to April 2026.

[2] 2026 Tech Leader Study: Building the IT foundation for agentic AI at scale IBM Institute for Business Value, 2026. Full report and executive interviews.

[3] CIOs are being held accountable for AI they don't fully control, IBM study finds CIO.com, June 2026. Source of the IDC and Greyhound Research analyst commentary and the 2027 agent-count figures.
