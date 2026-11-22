# GitAnalyze Mom Test Interviews: Full Transcripts

*Interview date: 2026-11-20. 10 interviews, sorted by first name. Interviewer: Yue.*

## Contents

- [Aisha](#aisha) (B3, Group B)
- [Dev](#dev) (A2, Group A)
- [Jordan](#jordan) (A4, Group A)
- [Kevin](#kevin) (B2, Group B)
- [Lin](#lin) (A3, Group A)
- [Maya](#maya) (A1, Group A)
- [Priya](#priya) (A5, Group A)
- [Rachel](#rachel) (B1, Group B)
- [Sam](#sam) (A6, Group A)
- [Tom](#tom) (B4, Group B)

---

## Aisha

*B3 · Group B · chooses tools for a team*

**1. Yue:** Thanks for making time. I'm researching how people choose open-source tools. I'm not selling anything. What are you working on right now?

**Aisha:** Sure, happy to. So I'm a business analyst at a consulting firm, mid-size, we do a lot of data and reporting work for clients. Right now I'm on a retail client, mostly dashboards and cleaning up how they report on inventory. Lots of stakeholder meetings, honestly. Less hands-on than people think.

**2. Yue:** Richard said you had to pick a tool for a client at some point. Tell me about the last time.

**Aisha:** Yeah, that was about five months ago. The data engineers on our team wanted to use dbt Core for the transformation layer. It's open-source, so it's free, and the client's leadership, the VP of data and a couple of directors, were nervous about it. They're used to buying things from a vendor. So I had to basically make the case that it was okay.

**3. Yue:** What was it for, exactly?

**Aisha:** Transforming the raw data in their warehouse into tables the dashboards could use. The engineers had used dbt before. My job was more the "why should the client be comfortable with this" part.

**4. Yue:** How did you go about making the case? Start from the beginning.

**Aisha:** So first I put together a short deck. Maybe five or six slides. One slide was who else uses it. You know, the logos. There are a lot of recognizable companies that use dbt, and there are case studies on their site. I pulled a couple that were similar to our client's industry.

**5. Yue:** Where did you find those?

**Aisha:** Their website mostly. And I think there was an analyst report that mentioned it, Gartner or Forrester, I don't remember which one. I just grabbed the line that said it was widely adopted.

**6. Yue:** Okay. What else was in the deck?

**Aisha:** The community size. They have a Slack community, and it's huge. Tens of thousands of members, I think. I took a screenshot of it. It shows there's a lot of people who can help if something goes wrong.

**7. Yue:** What did you look at to get that? Walk me through your screen.

**Aisha:** Honestly it was the dbt website, then the Slack join page that showed the member count, then I googled for case studies. I think the whole thing took me an afternoon, maybe half a day. I wasn't doing deep research. I was building a story.

**8. Yue:** Did you look at GitHub at any point?

**Aisha:** No, no. I mean, I know it's on GitHub. One of the engineers looked at that side. I didn't really know what I'd be looking for. I'd see code and a bunch of numbers and, I don't know, I wouldn't know what's good.

**9. Yue:** What did the engineer look at, do you know?

**Aisha:** Hm. I think he checked that it was actively updated? He said something like "it's alive, they release often." He told me that in a hallway chat, basically. It wasn't a formal thing. I didn't write it down.

**10. Yue:** So what did the client say when you presented it?

**Aisha:** They had two big questions. One, what about support? If it's free, who do we call when it breaks at two in the morning. And two, security. Where does the data go, does it leave our environment, who's accountable.

**11. Yue:** How did you answer the support one?

**Aisha:** There's a paid cloud version from the company that makes it, and also, there are consulting partners who offer support. So I said there's a paid path if you want it. And for security I got our engineer to explain that it runs inside the client's own warehouse, so the data doesn't go anywhere else. I wrote that up as a half page.

**12. Yue:** Did anyone ask about how popular it was, or how many people use it?

**Aisha:** Not really, no. I mean, the logos covered that, I guess. Nobody said "how many stars does it have" or anything like that. I actually had to look up what stars were, later, when the engineer mentioned it.

**13. Yue:** What do you mean?

**Aisha:** Oh, he said it had like a gazillion stars on GitHub, and I said, is that good? And he said it's like likes. I've seen it since but I don't use it for anything.

**14. Yue:** Who had the final say on the decision?

**Aisha:** The VP of data, ultimately. He cared about two things. Not being locked into something, and not getting blamed if it went wrong. Like, "can I defend this choice upstairs." So the logos really helped with that. If Company X uses it, nobody gets fired.

**15. Yue:** Did you write anything down, other than the deck?

**Aisha:** The half page on security, and there was an email thread. That was it. No big document.

**16. Yue:** Okay. Was there a time a team picked a tool and regretted it?

**Aisha:** Hm. Not on my projects. There was a colleague's project, a different team, they built something on a tool that had a free tier, and then the free tier went away. I think it was a hosting thing? I don't remember exactly. They had to rush to move things over. I only heard about it at lunch.

**17. Yue:** What happened after?

**Aisha:** I think they migrated to something else. It cost them a couple of weeks, I think? I'm not sure. It wasn't my project.

**18. Yue:** Has that changed how you check things?

**Aisha:** I mean, I think about it now, "is this thing going to start charging." But I haven't actually changed anything I do. It's more of a feeling.

**19. Yue:** When you picked dbt, did you look at other options?

**Aisha:** The engineers had a short list, I think there was one other. I didn't compare them myself. I just went with what the team was already comfortable with.

**20. Yue:** If the engineer hadn't looked at the GitHub side, what would you have done?

**Aisha:** Asked him to, probably. Or asked someone. I'd be a bit stuck, honestly. I don't know what I'd check myself. Is there something I should be checking? Like, what's a fork? I see that word and I have no idea.

**21. Yue:** Let's not worry about that. What would you have wanted to see?

**Aisha:** I guess whether it's going to be around in a few years. That's what the client really cares about. But I'd probably just ask the vendor, or ask an analyst. That's how we usually do it.

**22. Yue:** When did you last ask an analyst something like that?

**Aisha:** Oh, I don't, personally. We have a research team, sort of. I just meant in general. For dbt I didn't ask anyone, I just used the report that was already out.

**23. Yue:** Okay. Have you used any AI tools or plugins at work, like coding assistants?

**Aisha:** Copilot, a bit, in Excel and the like. And ChatGPT for drafting. But I've never installed anything beyond that. I don't write code really.

**24. Yue:** Okay, I'll skip that. Last thing before I let you go. Richard mentioned you know a few people who pick tools for client work. Would you be open to introducing me to one of them?

**Aisha:** Oh. Um. Maybe? I'd have to think about who. A couple of the engineers are the ones who actually choose, and they're slammed right now. Let me see. Send me a short note I can forward and I'll see who's around after the holidays.

**25. Yue:** That would help. Thanks, Aisha.

**Aisha:** Of course. Good luck with it. It sounds like an interesting project.


---

## Dev

*A2 · Group A · recently added a library, tool, or AI skill*

**1. Yue:** Thanks for making time. I'm researching how developers choose open-source tools and AI skills. I'm not selling anything. What are you working on right now?

**Dev:** Uh, I'm on co-op at a fintech here in Boston, backend, Python. This week it's mostly a reconciliation job that's failing on about 3% of records. So, debugging. I've got maybe fifteen minutes before standup prep, so.

**2. Yue:** Got it, I'll keep it short. Tell me about the last library you added to a project. What was it for?

**Dev:** Settings, config stuff. About two months ago. Our service had env vars read in like six different places, and I needed one place that loads them, validates types, and has defaults. So I added a settings library.

**3. Yue:** How did you find it?

**Dev:** Googled "python settings management" or something like that. Then a Reddit thread, I think r/Python. Somebody asked basically the same thing and there were like four or five answers.

**4. Yue:** Did you look at other options?

**Dev:** Yeah, two. There were two that kept coming up in the thread. I opened both GitHub pages.

**5. Yue:** Walk me through what was on your screen when you decided.

**Dev:** Okay so, GitHub repo page. I look at the README first, quickly. Then I look at the last commit date, and the open issues count. One of them had, I don't know, maybe 300 open issues, which looked kind of scary, but then I clicked in and a few had replies from the maintainer, so okay. The other one was smaller. Last commit was like two weeks ago on both, I think. Honestly they were pretty similar.

**6. Yue:** How long did that take?

**Dev:** Five minutes? Maybe a bit more. I wasn't going to spend an hour on a config library.

**7. Yue:** Why that one?

**Dev:** My mentor, he's the senior guy on my team, he'd heard of one of them. I mentioned the two names at lunch and he said "oh, that one, yeah, I've seen it around." So I went with that. It's not like I had a better reason.

**8. Yue:** If you hadn't found it, what would you have done?

**Dev:** Written a little class myself with os.environ and some dataclasses. Probably a day. It's not hard, it's just annoying to maintain.

**9. Yue:** Have you ever used a library or tool that stopped being maintained or broke? Tell me about the last time.

**Dev:** Oh yeah. Last year, a React side project. I was building a little scheduling thing with a friend, and I used a date-picker library. Then it got archived. And I didn't notice. I upgraded React, and the date picker just broke. Like, console errors, peer dependency stuff.

**10. Yue:** How did you find out it was archived?

**Dev:** I went to the GitHub repo to see why it broke and there was an issue, open for a few weeks, titled "Is this project dead?" And then I scrolled up and saw the little archived banner at the top. That's how I found out. Kind of embarrassing, honestly.

**11. Yue:** What did it cost you?

**Dev:** About two days. I had to find a replacement, install it, and then restyle everything because the new one had different markup and our CSS was tied to the old class names. Two days of a weekend, basically. It was a side project, so no one was paying me, but yeah. I was annoyed.

**12. Yue:** What do you do now to avoid that?

**Dev:** I check the last commit date. Like, within three months is fine. And I look at whether issues get replies. If there's like twenty issues with no response from anybody, that's a bad sign.

**13. Yue:** Was that what you did with the settings library?

**Dev:** Yeah, that's the thing I just described. Last commit, issue count, whether people answer. So yes.

**14. Yue:** Is there anything else you check?

**Dev:** Not really. I mean, I'm not super systematic about it. Sometimes I forget. Like for a small utility I'll just pip install and see if it works.

**15. Yue:** When was the last time you did that, just installed it?

**Dev:** Uh, a few weeks ago. A CSV helper thing. Didn't check anything, it's a dev dependency, who cares. If it breaks I'll just rip it out.

**16. Yue:** Have you installed any AI skills, plugins, rules, or MCP servers for Claude Code, Cursor, or similar?

**Dev:** No. We use Copilot at work, that's pretty much it, and that's the company-approved one. There's a policy, we can't just install random tools. Security would freak out. I have messed with Cursor on my own laptop for like an evening but I didn't add anything to it.

**17. Yue:** What was the evening about?

**Dev:** Just curiosity. Somebody in the co-op Slack was talking about it. I opened it, asked it to refactor some stuff from my React project, was kind of impressed, and then I went back to school work. Never went back.

**18. Yue:** Did you look for any rules files or extensions while you were in there?

**Dev:** No. I saw there was a thing for it, a marketplace or whatever, but I didn't click. I didn't have a reason.

**19. Yue:** Have you ever looked at how fast a project was growing, or at a trending list, when choosing something? When was the last time?

**Dev:** Growing. like stars? No. I mean, I see star counts. Everyone sees star counts. But growing over time, no, I never looked at that. GitHub trending, I've opened it a couple times scrolling, but not to choose something.

**20. Yue:** When was the last time you opened trending?

**Dev:** Maybe in the summer? Before co-op started. I was bored. Didn't install anything off it.

**21. Yue:** Ever looked at how many people download a package? Where?

**Dev:** Npm weekly downloads. It's on the npm page, right side. I've looked at it once or twice. Mostly I was just curious how big the thing was.

**22. Yue:** The last time, what was it for?

**Dev:** I think it was that date picker replacement, actually. After the archived one. I wanted to make sure the new one wasn't also some tiny thing nobody used. It had like a few hundred thousand weekly downloads and I went "okay, fine." Did it change my decision? I don't think so. I'd already kind of picked it.

**23. Yue:** And for Python, PyPI, anything like that?

**Dev:** Not really. PyPI doesn't show downloads on the page, right? I think you have to go to some other site. I've never bothered.

**24. Yue:** The last time you recommended a tool to your team, how did you make the case?

**Dev:** Oh, I'm an intern. I don't really recommend stuff. For the settings library I just opened a PR and put a sentence in the description. "Centralizes env loading, validation." My mentor approved it. Nobody asked anything, I think someone asked whether it was already in our requirements. It wasn't.

**25. Yue:** Did anyone push back on the choice itself?

**Dev:** No. I mean, he was the one who'd heard of it.

**26. Yue:** Have numbers like stars or downloads ever been misleading for you?

**Dev:** Hm. Not that I can think of. The date picker had a decent number of stars, I remember that. It was like four thousand or something. And it was still dead. So I guess stars don't tell you much about, whether it's alive. But I didn't think about it that way back then.

**27. Yue:** Has out-of-date information ever led you to a wrong choice?

**Dev:** Besides the date picker? Not really. Oh, tutorials, kind of. Stack Overflow answers using old versions of stuff. But that's different, I think. That's just annoying.

**28. Yue:** Okay, that's most of what I wanted to ask. One thing. Next time you choose a library or a skill, could I watch for ten minutes?

**Dev:** Um. Maybe? I mean, it's not like I do it that often. It's like once every month or two. And at work I probably can't share my screen with an outsider, because of, you know, the policy thing. Maybe a side project. Ping me on Slack later and I'll see.

**29. Yue:** Totally fine. Thanks, I'll let you get back to the reconciliation job.

**Dev:** Yeah, appreciate it. Good luck with the research.


---

## Jordan

*A4 · Group A · recently added a library, tool, or AI skill*

**1. Yue:** Thanks for jumping on. I'm researching how developers choose open-source tools and AI skills, nothing to sell. So, what are you working on right now?

**Jordan:** Oh nice, yeah, happy to. So I'm freelance, mostly small business sites, right now it's a booking site for a physical therapy place, Next.js, some Stripe stuff. Super normal. I also have a landscaping client that's like a four-page thing, almost done. I did a bootcamp like two years ago and basically just kept going from there.

**2. Yue:** Tell me about the last library, tool, or AI skill you added to a project. What was it for?

**Jordan:** Okay so, last month, I installed this Cursor rule pack for Next.js. It was all over X, like everybody was posting about it. It basically tells Cursor how to structure app router stuff, server components, naming, all that. I put it in the PT clinic project.

**3. Yue:** How did you find it?

**Jordan:** X. Somebody I follow quote-posted it, and it had like, I don't know, thousands of likes? Then I went to the repo.

**4. Yue:** What did you look at before deciding? Walk me through what was on your screen.

**Jordan:** Um. So the post first, and the likes were crazy. Then I clicked through to GitHub, and I looked at the star count, which was high, I think like eight or nine thousand? And then I scrolled the README, it had a nice little before-and-after example. And I think I glanced at the folder structure. Then I just copied the rules folder into my project.

**5. Yue:** How long did that take?

**Jordan:** Like ten, fifteen minutes? Maybe less. It's just markdown files, right, it's not like it's going to break anything.

**6. Yue:** Did you look at other options?

**Jordan:** Not really. I think there were a couple other rule packs in the replies, but this was the one everybody was talking about. Oh, and I did search the Cursor Discord for it, and someone said it was good. So that.

**7. Yue:** Why that one?

**Jordan:** Honestly, because it was the one. Like if everybody's using it, there's probably a reason, you know? And it looked really polished.

**8. Yue:** Have you ever used a library or tool that stopped being maintained or broke? Tell me about the last time.

**Jordan:** Oh man, yes. Okay, so there was this UI component library, it was trending big on GitHub like last spring, super pretty components, animations, the whole thing. I used it for a client, the dental office one, and then another site after that. And then like six months later I went to update something and, nothing. The last commit was months old, issues piling up, and it broke when I bumped Next.

**9. Yue:** How did you find out?

**Jordan:** I hit a bug with the new React version and went to file an issue, and that's when I saw there was like a hundred open ones and the maintainer hadn't replied in forever. Before that I had no idea.

**10. Yue:** What did it cost you?

**Jordan:** Time, mostly. I think about a week total, across the two projects? I had to rip out some components and replace them, and I had to email the client saying the launch of the new page was going to slip. That was an awkward email. They were fine about it but still, you don't want to be explaining that.

**11. Yue:** What do you do now to avoid that?

**Jordan:** Um. I mean, I look more carefully now? Like I try to, I don't know, check that it's active. I'll glance at the latest commit, maybe. I think. I mean for the rule pack I didn't really, because it's just markdown. But yeah, I'm more careful. Kind of.

**12. Yue:** When did you last do that, glance at the latest commit?

**Jordan:** Hmm. Let me think. Probably not since the dental thing, honestly. For the stuff since then I mostly went off, like, what felt solid. Is that bad?

**13. Yue:** Where do you usually hear about new tools?

**Jordan:** I check GitHub Trending a few times a week, kind of for fun. Like it's my coffee thing. And there's a newsletter I follow, I forget the name, it's a weekly JavaScript one, I think. Oh, JavaScript Weekly? Something like that.

**14. Yue:** Last time you found something on Trending, what was it?

**Jordan:** Okay so, a few months ago, there was this, I think it was a form validation thing, a small library, that was shooting up. I tried it in a side project. Still using it, actually. And there was another one, a CLI tool, that I used for like two weeks and then dropped because it was kind of buggy.

**15. Yue:** What made you try them?

**Jordan:** Seeing them go up, honestly. When something goes from nothing to like two thousand stars in a week, you're like, okay, what's this, I should know about this. I don't want to be the guy using old stuff while everyone else moved on.

**16. Yue:** Did that change what you picked, over something older?

**Jordan:** Yeah, probably? I mean, the validation one, I already had something I was using. But this one looked newer and cleaner and everybody was talking about it. So yeah, I switched. For the side project at least.

**17. Yue:** Have you installed other AI skills, plugins, rules, or MCP servers for Cursor or similar?

**Jordan:** A couple. I've got a Context7 MCP thing that I set up, I think someone in Discord posted it. And I tried some prompt packs for Claude, but those I took out because they made Cursor, like, over-explain everything. So I deleted them.

**18. Yue:** How did you decide the rule pack was worth trusting, before you installed it?

**Jordan:** I mean, the likes and the stars. And it's from a dev who has a big following. I didn't read all the rules or anything. I skimmed a few. Oh, and I did look at whether it had any, like, weird commands in it, but it's just text so I figured it was fine.

**19. Yue:** Have you ever gone looking for skills, or do you mostly install ones that show up in your feed?

**Jordan:** Mostly they show up. I did search once on GitHub for "cursor rules" and sorted by stars. That was kind of it. There's so many, and it's hard to tell which ones are actually good. I wish there was, like, a way to see which ones are good, you know? Like a leaderboard with reviews or something. Ooh, or a thing that scores them.

**20. Yue:** What would that let you do? When did you last need that?

**Jordan:** Um. I guess when I was picking that rule pack? But honestly I just went with the popular one, and it was fine. So maybe I didn't need it. I just think it'd be cool. I'd probably use it for fun, honestly, like the Trending thing.

**21. Yue:** Have numbers like stars or downloads ever been misleading for you?

**Jordan:** Hm. Well, the component library had tons of stars and then died. So, I guess yes? But it's not that the stars were fake, it was just that the guy stopped. I did hear that people buy stars, there was some article or a thread about it. But I've never checked. How would you even check?

**22. Yue:** Have you ever tried?

**Jordan:** No. I mean, I don't think any of the stuff I've used was fake. It all had real people talking about it.

**23. Yue:** The last time you recommended a tool to a client, how did you make the case?

**Jordan:** Oh, clients don't really care about that. They just want a site. I mean, I told the PT clinic owner we'd use Next and Stripe and she was like "okay, whatever's best." So I pick everything. The only time they care is when it's late.

**24. Yue:** Like the dental one.

**Jordan:** Yeah, exactly. That one they cared.

**25. Yue:** Did anything change in how you pick after that one?

**Jordan:** I guess I tell myself I'll check maintenance more. But then something shiny shows up on Trending and I'm like, okay but this one's so cool. Honestly the cool factor probably wins most of the time. I know that's not the best answer.

**26. Yue:** Last thing. Next time you're choosing a library or skill, could I watch for ten minutes? Just screen share, you doing what you normally do.

**Jordan:** Oh, yeah, totally! That sounds fun. I'm not sure when though, I've got the landscaping launch this week and then Thanksgiving. Maybe early December? Just DM me on Discord, I'm pretty much always on there. I don't really know anyone else who'd want to do this, my bootcamp group chat is dead. But yeah, DM me!

**27. Yue:** Great, I will. Thanks, Jordan.

**Jordan:** Awesome, good luck with it!


---

## Kevin

*B2 · Group B · chooses tools for a team*

**1. Yue:** Thanks for making time, Kevin. Quick intro: I'm a student at Northeastern, researching how developers and teams choose open-source tools and AI skills. I'm not selling anything. Mostly I want to hear what actually happened. So, what are you working on right now?

**Kevin:** Sure, happy to. Go Huskies and all that. So I'm a PM at a 25-person startup, we're in B2B workflow software, I'll skip the pitch. Right now it's mostly Q1 planning, a big onboarding revamp, and, honestly, wrangling engineering priorities. Which is the real job of a PM, right? Alignment. Are you building something, by the way? Because I'd love to hear what angle you're taking.

**2. Yue:** Just research for a class, nothing built. I'm curious about the tool-choosing part. When was the last time you recommended a tool to your team?

**Kevin:** Okay, so that would be about three months ago. We needed feature flags. We were doing releases kind of all-or-nothing, and I wanted us to be able to roll things out to ten percent of users, that kind of thing. I'm not the one who writes the code, but I own the rollout, so I pushed for it.

**3. Yue:** How did you find options?

**Kevin:** Googling, mostly. "Open source feature flag." And I asked in a couple of Slack communities. A few names kept coming up. Unleash, GrowthBook, Flagsmith. I'd heard of LaunchDarkly of course, but that's the paid one and the pricing was, you know, a conversation.

**4. Yue:** Walk me through what you did once you had those three names.

**Kevin:** So I made a slide. One slide, comparison table, three columns. I pulled GitHub stars, number of contributors, date of the last release, and whether there was a company behind it. And then I grabbed a screenshot from star-history.com, the one that overlays the growth curves, and dropped it at the bottom. It looked really clean. Honestly it was a good slide.

**5. Yue:** What was on your screen while you were putting that together?

**Kevin:** GitHub repo pages in three tabs, the star history site, Google Slides. Maybe the docs pages for a bit. I didn't go deep into the docs, to be honest. I'm not the one who has to integrate it. That's the engineers' thing.

**6. Yue:** How long did that take?

**Kevin:** Maybe an hour and a half? Two hours with the formatting. The formatting is always the part that eats the time.

**7. Yue:** Why those numbers in particular?

**Kevin:** Um. I mean, they're what you can see. Stars tell you people like it, contributors tell you it's alive, last release tells you it's not abandoned. It's kind of the standard stuff. I think people just expect to see them. The star chart especially, because a line going up and to the right, nobody argues with that.

**8. Yue:** So you took it to the team. What happened?

**Kevin:** I presented it at our weekly eng sync. And, okay, this is where it got interesting. Our CTO, he asked three things, and I remember them because they were so on the nose. "Who is behind this? Will it exist in two years? And can we self-host it?" And I'm like, well, I have the stars right here. And he said, "Stars don't tell me that."

**9. Yue:** What did you do then?

**Kevin:** I kind of scrambled. I said I'd follow up. I went back and looked at which of the three had an actual company behind it, funding, a real team, and whether there was a self-hosted option that wasn't some crippled version. That changed the shortlist. One of the three basically fell off because the hosted version was where all the good stuff was.

**10. Yue:** What did the stars tell you in that follow-up?

**Kevin:** Honestly, not much. They were roughly in the same ballpark for two of them. The company thing was the tiebreaker.

**11. Yue:** Did you put the follow-up in writing?

**Kevin:** Yeah, I added a second slide, then I sent a short Slack message summarizing. I used Claude for a bit of it, I use Claude in the browser a lot for drafting PRDs, so I had it help me tidy the writeup. But the facts, I went and checked those myself on the company sites.

**12. Yue:** Who had the final say?

**Kevin:** Technically the CTO. I recommend, he decides, and the rest of the team sort of nods. It's a small company, so it's not like there's a procurement process.

**13. Yue:** What did he care about most?

**Kevin:** Not getting stuck. He's been burned. We all have. Which, I should say, I have a story about that.

**14. Yue:** Tell me about that.

**Kevin:** So, previous job, a different company, a team adopted this dashboard tool. Cool product, everybody loved the demo. And about a year in, the company behind it pivoted. They went after enterprise, deprecated half of what we used, support got slow. We had to migrate, and it took a full quarter. A full quarter, for a dashboard tool! I wasn't the one who picked it, but I was the one who had to explain to leadership why the roadmap slipped.

**15. Yue:** How did you find out they were pivoting?

**Kevin:** A blog post, actually. A very "we're excited to announce" blog post. And then the changelog went quiet. That's the thing. The repo-ish signals looked fine until pretty much the moment it fell over.

**16. Yue:** What do you do now to avoid that?

**Kevin:** Now I ask the "who's behind it" question up front. Before the CTO has to ask it, ideally. Well, this last time he still had to ask it. But I'm getting better. Maybe. I don't have a formal checklist or anything.

**17. Yue:** Going back to the feature flag decision. When you say the company backing was the tiebreaker, how did that actually get decided? Where were you when it was settled?

**Kevin:** Oh. Hm. Okay, honestly? It was a quick conversation. Fifteen minutes, me and the CTO, after the sync, standing, well, on a call, we're remote. He just said, "Which one has a real company and a decent self-host story," I told him, and he said, "Fine, that one." The slides didn't really come up again.

**18. Yue:** So the slide, the table and the chart, where did that fit in?

**Kevin:** Look, I think it got me into the room. It made the recommendation look like I'd done the work. Which I had, sort of. But if I'm being straight with you, the chart didn't decide anything. It just made me feel prepared. And probably made the team feel like it was rigorous.

**19. Yue:** Got it. Has a team you were on picked a tool and regretted it, other than the dashboard one?

**Kevin:** Hm, small stuff. We had an analytics add-on that was fine for six months and then the pricing changed. That was more of a money thing than a switching thing. Nothing like the dashboard story.

**20. Yue:** Switching topics a little. Have you installed any AI skills, plugins, or MCP servers for Claude or similar tools?

**Kevin:** No, not really. I use Claude in the browser, like I said. Drafting PRDs, summarizing user interviews, rewriting my emails to sound less terse. I've heard about skills and plugins and all that. Our engineers use Cursor, I think, but I haven't installed anything myself.

**21. Yue:** Have you ever looked for any?

**Kevin:** Not really. If one of the engineers sent me something, I'd try it, probably. I just haven't had a reason to go hunting.

**22. Yue:** Okay. Back to numbers. Have stars or downloads ever steered you wrong?

**Kevin:** Steered me wrong, hm. I mean, I don't want to say "wrong." I think with the dashboard one, the traction was real, they had lots of users, and it still didn't save us. So popularity and survival aren't the same thing. But I couldn't tell you a time a star count directly misled me. I guess I've never gone looking for that.

**23. Yue:** When you're about to recommend something today, what's the first thing you check?

**Kevin:** Probably, you know, I'd probably check whether there's a company behind it and when the last release was. Then maybe the stars for the slide.

**24. Yue:** When did you last do that?

**Kevin:** That was the feature flag one, I guess. I haven't picked anything since. Oh, there's a session replay tool someone mentioned, but that's still at the idea stage.

**25. Yue:** Makes sense. That's basically everything I wanted to ask. One thing: I'm trying to talk to more people who pick tools for their teams. Would you be willing to introduce me to your CTO, or one other person who does this regularly?

**Kevin:** Ooh, the CTO. Hm. He's really slammed right now, it's the end-of-year crunch. I could ask around, let me think about who'd be good. Actually, send me a short note about what you're working on, a couple of lines, and I'll see who I can point you to. And if you're building something, I'd love to hear about it, I have some thoughts on how this could be a product. Like a dashboard that scores repos for risk. Just throwing that out there.

**26. Yue:** Thanks, I'll send the note. I appreciate your time, Kevin.

**Kevin:** Anytime. Good luck with the class.


---

## Lin

*A3 · Group A · recently added a library, tool, or AI skill*

**1. Yue:** Thanks for making time. I'm doing some research on how developers choose open-source tools and AI skills. Nothing to sell, I just want to hear how it actually goes. To start, what are you working on right now?

**Lin:** Sure. I'm a second-year PhD in the NLP lab here. Right now it's mostly an evaluation pipeline, running a few models over a benchmark we're extending and logging results. It's less glamorous than it sounds. A lot of it is plumbing.

**2. Yue:** Tell me about the last library, tool, or AI skill you added to a project. What was it for?

**Lin:** Um. Last one would be about three weeks ago. I installed a Postgres MCP server and a filesystem MCP server for that pipeline, so Claude Code could query the results database and read the output directories without me pasting things in. I'd say "skills," but, well, those are MCP servers, I know that's a different thing from a SKILL.md. I tend to use the word loosely.

**3. Yue:** How did you find them?

**Lin:** There's an "awesome" list on GitHub, awesome MCP servers, something like that. I found both there. I go through it when I have a specific need. I'd say I look at it once a month, roughly.

**4. Yue:** Did you look at other options?

**Lin:** For Postgres there were, I think, three or four listed. For filesystem, not really, there's the reference one and I just used that.

**5. Yue:** What did you look at before deciding? Walk me through what was on your screen.

**Lin:** Okay. So the awesome list entry, then I click through to the repo. First thing is who owns it. Is it an org I recognize or a personal account that was created last month. Then I open the source. For Postgres especially, because it's going to have the connection string. I'm not going to hand credentials to code I haven't skimmed. So I'd open the main server file and look at what network calls it makes and how it handles the config.

**6. Yue:** How long did that take?

**Lin:** For the Postgres one maybe twenty, twenty-five minutes? It wasn't that big. I didn't read every dependency, to be clear. I read the entry point and grepped for anything like fetch, requests, anything with a URL.

**7. Yue:** Why that one over the others?

**Lin:** It was from a known publisher, and the code was short enough that I could actually read it. One of the others was a single account with a lot of stars but I couldn't tell what it was doing without a longer read, so I skipped it.

**8. Yue:** You said stars. Where do they fit?

**Lin:** Stars are a rough filter. If something has eleven stars I'm a bit more suspicious, but I wouldn't pick on stars. I can't say it's a precise thing. Plenty of well-starred repos have been fine and plenty have been, hm, not great.

**9. Yue:** If you hadn't found those, what would you have done?

**Lin:** Written a small script. Honestly, it'd have been about an hour. The MCP route is more convenient but it's not like I couldn't do without.

**10. Yue:** Have you ever used a library or tool that stopped being maintained or broke? Tell me about the last time.

**Lin:** In research code, that's. fairly constant, but I don't think that's what you mean. Mostly I use whatever the paper's reference code uses. If the paper pinned some old version of a tokenizer library, I use that. So it's not me choosing, it's me inheriting. The last time something broke was a reference repo depending on a Hugging Face API that changed. I pinned the version, done. Maybe an hour.

**11. Yue:** How did you find out it broke?

**Lin:** It threw an import error. That's how you always find out.

**12. Yue:** What do you do now to avoid that?

**Lin:** Pin versions in the environment file. That's it, really. I don't have a system for maintenance status. I do glance at the last commit date.

**13. Yue:** Have you installed any AI skills, plugins, rules, or MCP servers for Claude Code, Cursor, or similar, other than those two? Tell me about the last one.

**Lin:** Those two were the last. Before that I had a Cursor rules file I copied from a repo. And I had a couple of other MCP servers, I don't remember the exact names. A browser one, a GitHub one.

**14. Yue:** One you tried and removed?

**Lin:** Yes. One MCP server, I'd rather not say which one off the top of my head because I'd get the name wrong. I removed it.

**15. Yue:** What happened?

**Lin:** I noticed it was making requests to a host I didn't recognize. I was looking at network activity for something unrelated, and there it was, telemetry going to some domain. Nothing in the README about it.

**16. Yue:** How did you notice?

**Lin:** I had a traffic monitor running for a different reason. Otherwise I wouldn't have seen it. That's the part that bothers me, really.

**17. Yue:** What did it cost you?

**Lin:** An afternoon, probably. I had to figure out what was sending what. Whether it had picked up anything from my working directory. I read through the source properly that time and traced the call. I couldn't tell conclusively what had been sent, so I rotated a couple of keys to be safe. That was maybe two hours of the afternoon on its own.

**18. Yue:** What do you do now?

**Lin:** I prefer official publishers or at least well-known ones. Before, I was a bit looser about it. And anything touching files or credentials, I read the source. That's why the Postgres one took twenty-five minutes.

**19. Yue:** Before installing, how did you decide it was worth trusting, in general?

**Lin:** Publisher first. Then source if it touches files or secrets. Then stars, loosely. Sometimes I'll check whether there are open issues about network behaviour, but that's not systematic.

**20. Yue:** Do you go looking for new skills, or mostly install ones someone sends you?

**Lin:** I go looking, but not often. Monthly-ish through the awesome lists. And there's a channel in our lab Slack where people post things. If someone I know posts something I'll look at it, but I still read it myself. I don't take their word for it.

**21. Yue:** Have you ever looked at how fast a project was growing, or at a trending list, when choosing something? When was the last time?

**Lin:** No. I don't use trending pages. I mean, I've seen GitHub trending, but I couldn't tell you the last time I opened it. A project trending says people are looking at it, which isn't the same as it being safe. Different question.

**22. Yue:** Ever looked at how many people download a package?

**Lin:** Sometimes for PyPI packages, the download count. Honestly I don't remember the last time that affected a decision. It's more of a sanity check. I wouldn't claim it did anything.

**23. Yue:** The last time you recommended a tool to your team, how did you make the case?

**Lin:** Um, "team" is a loose word. It's a lab. I told the lab Slack about the filesystem and Postgres setup, I think? Two sentences. I said what it did and that I'd read the source. One person asked whether it worked with Cursor too. I said I'd only tried it with Claude Code, so I didn't know.

**24. Yue:** What did people push back on?

**Lin:** Nobody pushed back, to be honest. One labmate said he'd just write his own queries. Which, fair.

**25. Yue:** Did you put anything in writing?

**Lin:** Only that Slack message. No doc.

**26. Yue:** Who has the final say?

**Lin:** Everyone's on their own machine, basically. My advisor doesn't care what tools I use as long as the numbers are right. So nobody, in practice.

**27. Yue:** Has anything like stars or download numbers been misleading for you?

**Lin:** I'd say stars are easy to inflate and I know that, so I don't lean on them. Whether it's misled me specifically, I can't point to a case. The telemetry one wasn't a numbers thing, it just looked fine from the outside.

**28. Yue:** And out-of-date information leading you to a wrong choice?

**Lin:** READMEs that describe a config format that's changed, yes. That happens. Small stuff, not a wrong choice exactly. I'd waste ten minutes.

**29. Yue:** That's helpful. One last thing. Next time you go to choose a library or skill, could I watch for ten minutes?

**Lin:** Hm. Possibly. The thing is I only do it roughly once a month, so it'd depend on timing, and a lot of it is me reading source in silence, which probably isn't very interesting to watch. If you message me when you're ready I'll see where I am. I can't promise.

**30. Yue:** Okay, thanks, I will. That was really useful.

**Lin:** No problem. I hope the research goes well.


---

## Maya

*A1 · Group A · recently added a library, tool, or AI skill*

**1. Yue:** Thanks for doing this. I'm just researching how developers choose open-source tools and AI skills, nothing to sell. So, what are you working on right now?

**Maya:** Oh, of course, happy to! So it's a class project, a kind of study planner web app, React on the front. I'm in the MS CS program, first year, I did economics for undergrad so honestly everything is new to me, I basically use Claude Code for everything. Like, everything.

**2. Yue:** Everything, like what?

**Maya:** Like, setting up the repo, writing components, fixing errors. I'll paste an error in and it just goes. It's kind of amazing. I don't think I'd be able to do the project without it.

**3. Yue:** Tell me about the last library, tool, or AI skill you added to the project.

**Maya:** Hmm, okay, so last week. A classmate put a link in the course Slack to this frontend design skill. Something about making the UI look nicer, less like default AI stuff? I installed it right away.

**4. Yue:** How did you find it?

**Maya:** Just that Slack message. Someone posted it, and like five people reacted with the little eyes emoji and said they were using it, so I did too.

**5. Yue:** What did you do when you saw the link?

**Maya:** I clicked it, I think? It went to GitHub. And then I just copied the install command, I think it was one line you paste into Claude Code. Took maybe two minutes. I didn't really scroll the page.

**6. Yue:** What was on the page, as far as you remember?

**Maya:** Um. A lot of files? A README, I guess. I honestly just looked for the part that said how to install. That sounds bad, but everyone was using it, so it felt fine.

**7. Yue:** Did you look at any other options?

**Maya:** For the skill? No. I didn't know there were other ones. Are there? Like, other design skills? That sounds so useful, actually, like a list of them.

**8. Yue:** Did you look for a list at the time?

**Maya:** No, no. It was just, here's the thing, install the thing.

**9. Yue:** How long from seeing the message to having it working?

**Maya:** Like, honestly, five minutes? Including me getting distracted by another Slack thread.

**10. Yue:** What happened after you installed it?

**Maya:** I asked Claude to redo my dashboard page and it looked way better. Less purple gradient, which I was kind of sick of. So, yeah, it worked.

**11. Yue:** Okay. Let's go to something else in that project. What's the last library you added?

**Maya:** Oh, state management. So, I had props going everywhere and Claude said it was getting messy. So I asked it, what should I use for state in React. And it said Zustand. So I used it.

**12. Yue:** What was on your screen when you decided?

**Maya:** Just the Claude Code terminal. It gave me a short explanation, like why Zustand is simple, not a lot of boilerplate, and then it wrote the store for me. I think I ran the install and it was done.

**13. Yue:** Did you look at anything else besides that?

**Maya:** No. I think it mentioned Redux, like in passing? I'd heard of Redux in a class thing. But it said Zustand was lighter so I just went with that.

**14. Yue:** How long did that take?

**Maya:** Ten minutes maybe? Most of that was waiting for it to refactor stuff.

**15. Yue:** If Claude hadn't suggested Zustand, what would you have done?

**Maya:** Ooh. I mean, I'd probably Google it? Or ask a friend in the program. Or I'd probably look at what the tutorial used, I was following this YouTube tutorial at first. I don't know, I haven't really been in that spot yet.

**16. Yue:** Have you ever used a library or tool that broke or stopped working? Tell me about the last time.

**Maya:** Yes! Okay, this was, like, October maybe. I was following a tutorial, it was a React thing, and I copied the code and it just didn't run. Errors everywhere. And I was so confused because it's the tutorial's code, right?

**17. Yue:** What did you do?

**Maya:** I pasted the errors into Claude and asked it to fix it. And it tried a few things and some were wrong. Like it gave me code that also didn't work. It took me the whole evening, honestly. I was so annoyed. Claude kept being wrong about it.

**18. Yue:** How did you find out what the problem actually was?

**Maya:** Eventually it said something about, uh, a version change? Like the library had changed how something worked since the video. But I don't really know, it kind of fixed itself in the end. I just thought the AI was having a bad day.

**19. Yue:** What do you do now to avoid that?

**Maya:** Um, nothing really? I mean, I try to use newer tutorials? Or I just go straight to Claude and skip the tutorial. That's easier honestly.

**20. Yue:** Okay. Have you installed any other AI skills, plugins, or MCP servers for Claude Code?

**Maya:** Just that design one, I think. Oh, and I think there's some GitHub thing that Claude suggested connecting? I said yes and it was fine. I don't really remember what it does.

**21. Yue:** Tell me about that one.

**Maya:** Uh, I think it was when I was pushing code and it said do you want to set up something to access GitHub. I said sure. That's all I remember, sorry.

**22. Yue:** That's fine. For the design skill, before you installed it, how did you decide it was okay to trust?

**Maya:** I mean, my classmates were using it. And it was on GitHub, so, I guess it's real? I didn't really think of it as a trust thing. It's just text files, right?

**23. Yue:** Is it?

**Maya:** I think so? I mean, I'm not sure what's actually in it. Oh, that's kind of a good question. I never opened it.

**24. Yue:** Have you ever tried one and removed it?

**Maya:** No. I've never removed any. I didn't even know you could, I guess? I'd have to ask Claude how.

**25. Yue:** Have you ever gone looking for new skills yourself, or only install ones people send you?

**Maya:** Only ones people send me. I've never searched. I wouldn't know where to start, honestly. Is there a place? That sounds so useful.

**26. Yue:** Where would you start, if you had to?

**Maya:** Probably Google "Claude Code skills". Or ask in the Slack. Or ask Claude.

**27. Yue:** Have you ever looked at how fast a project was growing, or a trending list, when you chose something?

**Maya:** Like GitHub trending? I know that exists. I've seen it when someone shared a screenshot. I haven't used it myself to pick anything, I don't think.

**28. Yue:** Ever looked at how many people use or download a package?

**Maya:** Hmm. Not that I can think of. I think npm shows that? Someone mentioned it once. I haven't really looked.

**29. Yue:** What about stars on GitHub?

**Maya:** I mean, I know stars are a thing. I'd definitely check stars next time, that seems like an obvious thing to do. I feel kind of silly saying I didn't.

**30. Yue:** When did you last check stars on anything?

**Maya:** Um. Never, actually. I guess I've seen the number at the top of a page, but I never used it for anything. When I look at the skill's page I think it had a big number, maybe? I didn't really register it.

**31. Yue:** The last time you recommended a tool to a teammate, how did you make the case?

**Maya:** Oh, I'm on a team of three for the project. I didn't really recommend anything. I told them I was using Zustand and they said okay. One of them is more into backend, so they didn't care.

**32. Yue:** Did anybody push back?

**Maya:** Not really. One teammate asked if it was the Redux thing and I said no, it's a different one, simpler. And that was it.

**33. Yue:** Did you write anything down?

**Maya:** No. Well, there's a README Claude made, and maybe it mentions Zustand in there. I didn't write it myself.

**34. Yue:** Has a number like stars or downloads ever been misleading for you?

**Maya:** I don't think I've used them enough to be misled! If that makes sense. Oh, but I guess the thing with the tutorial. It looked fine, the video had a lot of views, and then the code didn't work. Is that the same kind of thing? I don't know.

**35. Yue:** What do you think was going on there?

**Maya:** The video was old? I didn't look at the date. I just assumed since it had a lot of views it was good. I never thought about that until right now.

**36. Yue:** Anything else about picking tools that's been annoying lately?

**Maya:** Honestly, not really? The main annoying thing is when Claude gives me stuff that doesn't run. Otherwise it's pretty smooth. I guess I'd like to know if what I'm using is, like, good? But I don't know how I'd even find that out. I'd probably just ask Claude.

**37. Yue:** Last thing. Would you be up for me watching for ten minutes the next time you pick a library or skill?

**Maya:** Oh, sure, yeah, that sounds fun. Just message me. I mean, I'm not sure when the next one will be, we're wrapping up the project soon. But yeah, definitely, I'd be happy to.

**38. Yue:** Great. Thanks, Maya.

**Maya:** Of course! Good luck with your research!


---

## Priya

*A5 · Group A · recently added a library, tool, or AI skill*

**1. Yue:** Thanks for making time. I'm just talking to people about how they pick open-source tools. I'm not selling anything. So, what are you working on right now?

**Priya:** Mostly my capstone. I'm in the MS Information Systems program, at the Arlington campus. We're building a dashboard for a nonprofit. It's, um, wrapping up now, so a lot of it is the final report.

**2. Yue:** What's the dashboard for?

**Priya:** They track program attendance across a few sites. Right now it's all spreadsheets. So we pull the data and show charts, by site and by month, that kind of thing.

**3. Yue:** Tell me about the last library you added to that project. What was it for?

**Priya:** The charting library. Plotly. We needed charts in Python, and I was the one who looked into it.

**4. Yue:** When was that?

**Priya:** About six weeks ago? Early October, I think. Maybe a bit before that.

**5. Yue:** How did you find it?

**Priya:** I mean, I'd heard of both of them already. Plotly and Altair. I searched "python charting library dashboard" and then those came up, and some blog comparisons. I think one was on Medium.

**6. Yue:** Did you look at other options besides those two?

**Priya:** Matplotlib, but only for a second. It's not really interactive. So it was those two.

**7. Yue:** Walk me through what was on your screen when you were deciding.

**Priya:** Okay. So, I had the GitHub page for each one open. Side by side, two tabs. I looked at the stars, and when the last release was. Then the documentation for both. And then I opened pepy.tech for the monthly downloads.

**8. Yue:** What did you look at first?

**Priya:** The docs, probably. Actually no, the GitHub page first. The README. Then docs. I'd say the docs mattered most to me, honestly. I tried to find an example close to what we needed. A bar chart with filters.

**9. Yue:** Did you find one?

**Priya:** In Plotly, yes. Altair's examples were nice but the interactive part was less obvious to me. I might have just not looked hard enough.

**10. Yue:** How long did all that take?

**Priya:** About an hour. Maybe a bit more.

**11. Yue:** Why Plotly, in the end?

**Priya:** The docs had more examples I could copy. And it's more widely used. It had more stars, and the downloads were higher.

**12. Yue:** When you say more widely used, what do you mean?

**Priya:** Just, the numbers. Plotly was, I don't remember exactly, something like tens of millions a month on pepy. Altair was less. I could look.

**13. Yue:** Did that number change what you picked?

**Priya:** Hmm. I don't think so, actually. I was leaning Plotly because of the docs already. The downloads were more like, confirming.

**14. Yue:** Okay. You went to pepy.tech specifically. Why that, instead of just the stars?

**Priya:** Oh. So our sponsor has an IT contact. He's the one who'd eventually have to maintain it, or his team would. And in one of our meetings he asked, "is this widely used?" Like, is it a safe thing. And I didn't have an answer in the moment. So I wanted a number to give him.

**15. Yue:** What did you do with the number?

**Priya:** I put it in the report. There's a small table, two rows. Stars and monthly downloads. Plotly, and I think Altair in the second column. With the date I checked.

**16. Yue:** Did he say anything about it?

**Priya:** He said okay. I think he was fine with it. He didn't ask anything more.

**17. Yue:** If you hadn't found Plotly, what would you have done?

**Priya:** Probably asked ChatGPT to recommend one. Honestly I did ask it too, at the start. It said Plotly or Altair, which is kind of how I got to those two. I don't remember if that was before or after the Medium thing.

**18. Yue:** What did you do with what ChatGPT said?

**Priya:** Just treated it as a starting list. I didn't trust it on versions or anything. It's sometimes out of date on code.

**19. Yue:** Have you ever used a library or tool that stopped being maintained, or broke on you? Tell me about the last time.

**Priya:** Not abandoned, no. Not that I've run into yet. I've had one with really bad documentation. That cost me a weekend.

**20. Yue:** Tell me about that one.

**Priya:** It was last spring, in a class project. A Python package for, um, parsing some kind of survey file format. I can't remember the name now. The README was three lines. I spent a Saturday and most of Sunday guessing what the function arguments were. Reading the source.

**21. Yue:** How did you find out the docs were that bad? Before or after you'd committed to it?

**Priya:** After. I'd only looked at the stars, and it looked fine. Then I started coding and it was like, oh no.

**22. Yue:** What do you do now to avoid that?

**Priya:** I read the docs first. Before anything else. That's why the docs were the first thing I checked on the charting one. I look for examples I can run.

**23. Yue:** Anything else you check now?

**Priya:** The last release date. If it's more than a year ago I get nervous. But I haven't actually rejected anything for that yet.

**24. Yue:** Have you installed any AI skills, plugins, rules, or MCP servers for Claude Code, Cursor, or anything like that?

**Priya:** No. I only use ChatGPT, in the browser. I copy code in and out.

**25. Yue:** Have you looked into those tools, or just not had a reason?

**Priya:** I've heard of Cursor. A classmate uses it. I haven't had a reason to switch, I guess. The browser works.

**26. Yue:** Okay. Back to the charting one. Besides that, have you ever looked at how fast a project was growing, or a trending list, when choosing something?

**Priya:** Like GitHub trending? I've looked at it, but just browsing. I never picked anything from there. I don't think I've used the star history graphs. I know people post those.

**27. Yue:** When did you last look at GitHub trending?

**Priya:** Hmm. Months ago. Maybe over the summer, when I was bored. Not for a project.

**28. Yue:** Okay. The last time you recommended a tool to your team, how did you make the case?

**Priya:** That was the charting library, too. We're four people. I told them in our Slack, "I looked at Plotly and Altair, I think Plotly is better because of the docs and it's more widely used," and I put the link to the docs page.

**29. Yue:** What did people say?

**Priya:** One teammate asked if Plotly would work with Streamlit, which we were using. I checked and it did. Another one, Marcus, said he'd used Altair before and liked it. But he didn't push.

**30. Yue:** Did you put anything in writing besides Slack?

**Priya:** The report, with the table. And a short section about why we chose it. A paragraph.

**31. Yue:** Who had the final say?

**Priya:** Technically our advisor, but he left it to us. The sponsor's IT guy cared about whether it's something that will keep working. That's what he kept asking about, kind of. Whether somebody can maintain it after we leave.

**32. Yue:** And how did you answer that?

**Priya:** With the table, mostly. And I said it's got an active release schedule. I'd checked the releases page, so that was true.

**33. Yue:** Has a team ever picked a tool and regretted it?

**Priya:** In a class last year, someone picked a database thing that none of us knew. It was slow going. But that wasn't me. I don't think they compared much.

**34. Yue:** Have numbers like stars or downloads ever been misleading for you?

**Priya:** Hmm. Not that I noticed. Well. I did wonder, with pepy, whether the downloads include like, automated things. CI systems. I read that somewhere. But I didn't go deeper. It was just a number for the report.

**35. Yue:** Did that bother you at the time?

**Priya:** A little. I added "approximate" in the caption. But, you know. He wanted a number.

**36. Yue:** Has out-of-date information ever led you to a wrong choice?

**Priya:** The ChatGPT code. It gave me a Plotly function once that was deprecated, I think. It still ran but gave a warning. I just fixed it. Not a big deal.

**37. Yue:** Okay. Is there anything about how you pick libraries that I should have asked and didn't?

**Priya:** I don't think so. It's not very complicated, I think. I just try to be careful. I like to have something I can point to.

**38. Yue:** Last thing. Next time you're choosing a library, could I sit in for ten minutes and watch how you do it?

**Priya:** Um. Maybe? I'm not sure when that would be. The capstone is basically done, so after that I might not pick anything for a while. Can you send me a message closer to then?

**39. Yue:** Sure, I'll do that. Is there a good way to reach you?

**Priya:** Email's fine. I'll put it in the chat.

**40. Yue:** Thanks, Priya. That was really useful.

**Priya:** Sure. I hope it helps with your project.


---

## Rachel

*B1 · Group B · chooses tools for a team*

**1. Yue:** Thanks for making time, Rachel. I'm researching how developers choose open-source tools and AI skills. I'm not selling anything, I'm just trying to learn. To start, what are you working on right now?

**Rachel:** Mostly planning, honestly. Q1 roadmap is due in two weeks. On the technical side, we're finishing the move of our billing service onto the new job queue, so I'm in a lot of standups about that. Not much hands-on code this month.

**2. Yue:** You mentioned the job queue. When did you pick that?

**Rachel:** Four months ago, around July. We were on an older Redis-based queue library that was getting painful. Retries were flaky and nobody wanted to touch it.

**3. Yue:** Walk me through how that decision actually happened. Who started it?

**Rachel:** One of my senior engineers, Dan, brought it up in a retro. I told him to write up options. He looked at three libraries and put together an ADR, an architecture decision record. Two or three pages in Confluence.

**4. Yue:** What was in it?

**Rachel:** Let me think. There was a comparison table. License, because legal requires us to check that. Security scan results from our scanner. Maintenance status: how often they release, how many maintainers, whether there are open security advisories. Whether a company backs it. And whether anyone on the team already knows it. Then a recommendation.

**5. Yue:** Was that the format Dan chose, or a standard one?

**Rachel:** We have a template, but the criteria section is up to the author. Dan used what we've used before. I think the maintenance part is something I pushed for a few years ago.

**6. Yue:** Why did you push for it?

**Rachel:** We got burned. Two years ago we were using an HTTP client library, and it got deprecated. Not abandoned overnight, just a notice in the README one day that it was in maintenance mode and to move to the successor.

**7. Yue:** When was the last time that came up for you, before the job queue?

**Rachel:** That was it, the HTTP client. We had it in three services. Migrating took most of a sprint, I'd say. Maybe eight or nine working days total across the people involved. Plus we had to retest everything that made outbound calls.

**8. Yue:** How did you find out it was deprecated?

**Rachel:** Someone saw it on the repo page while looking at an unrelated bug. Dependabot didn't flag it, because there was no vulnerability, just a deprecation. That's the annoying part. It wasn't in any alert.

**9. Yue:** What did that cost you, beyond the sprint?

**Rachel:** We pushed a feature a couple of weeks. I had to explain that to product. Nobody was thrilled.

**10. Yue:** What do you do now to avoid that?

**Rachel:** The maintenance criteria in the ADR, basically. And Dan runs through the repo's recent commits and issues for the shortlist. It's manual. We don't have anything that tells us when a dependency we already use starts going quiet.

**11. Yue:** So for the dependencies you already have, how would you know today?

**Rachel:** Honestly, probably the same way, someone notices. Dependabot covers vulnerabilities and version bumps. The scanner covers licenses and CVEs. Neither says "this project hasn't had a commit in eight months."

**12. Yue:** Back to the job queue. When Dan was looking at the three options, what was on his screen, as far as you know?

**Rachel:** The GitHub repo pages mostly. Releases tab, the security tab for advisories, the contributors list. He also ran the candidates through our internal dependency scanner and Snyk. Those results went into the ADR.

**13. Yue:** Did he look at anything else? Docs, blog posts?

**Rachel:** Docs, yes. And he did a small spike with the top two to see how the API felt. That took him maybe two days.

**14. Yue:** How long was the whole decision, from retro to approval?

**Rachel:** About three weeks. Most of it waiting on the security review, not the actual research.

**15. Yue:** What happened in the security review?

**Rachel:** Our security team looked at the scan output and the advisory history. They had one question about a transitive dependency, and Dan showed it was a dev dependency only. Then they signed off. Legal had already cleared the license.

**16. Yue:** Who had the final say?

**Rachel:** I approve it as the tech lead. But legal and security can veto. If either says no, it's dead, no matter what I think.

**17. Yue:** What did they care about most?

**Rachel:** Legal cares about license, only license really. Security cares about known vulnerabilities and whether the project responds to them. Whether there's a patch history. I'd say they care less about the library being good and more about it not creating a problem for them later.

**18. Yue:** When you made the case to the team, what did people ask or push back on?

**Rachel:** Mostly operational stuff. Does it need a new piece of infrastructure? Can we migrate incrementally? One engineer asked if we should just pay for a hosted service instead. That took a day of discussion.

**19. Yue:** Did anyone ask about popularity, how widely it's used?

**Rachel:** Not really. I mean, GitHub stars were in the table. One line. Nobody discussed it.

**20. Yue:** Why was it in the table if nobody discussed it?

**Rachel:** I think Dan just included it for completeness. It's visible on the page. I wouldn't call it a deciding factor. A lot of stars doesn't tell you much about whether someone will still be maintaining it in two years.

**21. Yue:** Did you look at how fast any of them were growing, or any trending list?

**Rachel:** No. That's not something I've done for work. Maybe for fun on a weekend, looking at what's on the GitHub trending page. Not for a decision.

**22. Yue:** Did you put the decision in writing anywhere besides the ADR?

**Rachel:** The ADR is the record. I added a short note in the engineering channel when it was approved. That's it.

**23. Yue:** Has a team ever picked a tool and regretted it?

**Rachel:** The HTTP client, in a way. Although at the time it was a reasonable choice. It was popular and well regarded. It just ended. I don't know that we'd have caught it earlier with a better process.

**24. Yue:** Anything else where the information was out of date or misleading?

**Rachel:** Hmm. Not that I can think of right now. Once we found a package whose README said it was actively maintained, but the last release was a year old. We caught that during the review, so no harm done.

**25. Yue:** What did you do when you saw that?

**Rachel:** Dropped it from the list. Didn't spend time on it.

**26. Yue:** Switching topics a little. Have you installed any AI skills, plugins, or MCP servers for Claude Code, Cursor, anything like that?

**Rachel:** Not for work. I personally use GitHub Copilot, in the editor. The company hasn't approved anything like Claude Code skills or MCP servers yet. I know people are asking.

**27. Yue:** Who would decide on that?

**Rachel:** Security, mainly. They'd have to look at what data goes where. I think there's a working group, but I haven't been in it.

**28. Yue:** Have you tried any yourself at home?

**Rachel:** No. I've seen some things people share on LinkedIn, but I haven't installed anything.

**29. Yue:** When something like that comes up, how do you think your team would evaluate it?

**Rachel:** I'd guess the same process, license, security, whether it's maintained. But I'd be speculating. We haven't done it.

**30. Yue:** Understood. Let's stay with what you've actually done. For the next library you evaluate, who will do the work, Dan again?

**Rachel:** Probably whoever raises it. It rotates.

**31. Yue:** That's helpful. One last thing. Would you be open to an intro to someone else who picks tools more often than you do, or would it be easier if I sat in on the next time your team evaluates something for ten minutes?

**Rachel:** I can think about the intro. There's a platform engineering lead, Marcus, who handles more of the shared tooling decisions. I'd have to ask him first. Sitting in on an evaluation, probably not, there's confidential stuff in there and I'd have to run it by security. Send me a short email and I'll see.

**32. Yue:** That works. Thanks, Rachel.

**Rachel:** Sure. Good luck with the project.


---

## Sam

*A6 · Group A · recently added a library, tool, or AI skill*

**1. Yue:** Thanks for jumping on. So I'm researching how developers choose open-source tools and AI skills. Nothing to sell, I'm just trying to understand what people actually do. To start, what are you working on right now?

**Sam:** Sure. Day job, I'm a senior engineer at a healthtech company here in Boston, so mostly backend stuff, a FHIR integration layer, some very boring but important data validation. Outside of work I mess around with Claude Code a lot, which is why I'm on r/ClaudeAI. Can I ask why you're interested in how people choose tools? Is this for a class?

**2. Yue:** Yeah, it's for a class. I'm just trying to learn how the choosing actually goes. Tell me about the last library, tool, or AI skill you added to a project. What was it for?

**Sam:** Last week I installed a skill from Anthropic's official skills repo. I'm blanking on which one at the moment, it was one of the document ones, I think the PDF one. I had a pile of scanned referral forms I wanted to pull text out of for a side project. Nothing at work, that would never get through compliance.

**3. Yue:** How did you find it?

**Sam:** It's in the official repo. Anthropic's GitHub. I knew it was there already, I'd seen it mentioned a few times on the subreddit. So I didn't really go hunting.

**4. Yue:** Did you look at any other options?

**Sam:** Briefly. There's a bunch of PDF-ish skills floating around from random people. I opened two or three and closed them. Honestly I'd probably have just written my own if the official one hadn't existed. I write most of my own skills and rule files anyway.

**5. Yue:** What did you look at before deciding to install the official one? Walk me through what was on your screen.

**Sam:** Okay, so, I opened the folder on GitHub. Read the whole SKILL.md. Then I looked at the scripts it ships with, there were a couple of Python files, and I read those too, line by line, because I'm not running something on my machine that I haven't read. I checked what it shells out to, whether it makes any network calls. It doesn't. Then I copied it into my skills directory by hand instead of using any installer thing.

**6. Yue:** How long did that take?

**Sam:** Fifteen, twenty minutes? Maybe less. The scripts were short. Longer if it were someone else's repo, I'd read the commit history too.

**7. Yue:** Why that one over the others you opened?

**Sam:** Because it's from Anthropic and I could read all of it. That's it. It's not like I trust Anthropic blindly, I just trust them more than "ai-superskills-pro" with a logo.

**8. Yue:** If it hadn't existed, what would you have done?

**Sam:** Written my own. Or used pdftotext and OCR directly. It's not magic.

**9. Yue:** Have you ever used a library or tool that stopped being maintained or broke? Tell me about the last time.

**Sam:** Oh, plenty. Last time that really bit me. a date-parsing library at work, maybe a year and a half ago. Maintainer disappeared. A new Python version came out and it started throwing deprecation warnings, then outright broke on 3.12 I think. We had it pinned in three services.

**10. Yue:** How did you find out?

**Sam:** CI failed when someone bumped the base image. Not a fun Monday.

**11. Yue:** What did it cost you?

**Sam:** A couple of days across two people, I guess. Swapping it out wasn't hard, it was just finding every place it was used. Nothing dramatic. The annoying part was I'd said at the time that it was a risk and nobody wanted to hear it.

**12. Yue:** You said you flagged it at the time. What did you look at back then?

**Sam:** Contributors, mostly. It was basically one guy. Single maintainer. That's the thing I look at first for anything going into production. Then issue response time, are issues just sitting there for months, and release cadence. If the last release was two years ago, that's a smell. I actually argued against that library in the original review. I lost, because it was convenient and the API was nice.

**13. Yue:** Where do you look for those things? Walk me through the last time you did it.

**Sam:** GitHub, the Insights tab for contributors, kind of squint at it. The issues page sorted by recently updated. Releases page. Sometimes the commit graph. It's all manual. I don't have a system, I just open like six tabs.

**14. Yue:** Have you installed any AI skills, plugins, rules, or MCP servers for Claude Code or similar, besides that one? Tell me about the last one before it.

**Sam:** Besides the PDF thing? A few MCP servers, a GitHub one and a Postgres one, early this year. Again from the official-ish repos. Everything else I've written. I've got maybe fifteen skills of my own and some CLAUDE.md rule files. I don't trust random ones. They're basically prompts that can run code. People treat them like npm packages and they're not, they're more dangerous.

**15. Yue:** Where do you usually find new ones?

**Sam:** Reddit, mostly. People post their stuff. I look at what they've done, steal the ideas, and rewrite them. I'd never install one directly. Well. I've installed maybe two from other people, and I read every line.

**16. Yue:** Have you tried one and removed it?

**Sam:** There was one for "code review", a rules file somebody on the subreddit shared. It was like four hundred lines of "you are a world-class engineer" fluff. I tried it for an afternoon. Deleted it. It made the output worse, honestly. Too verbose.

**17. Yue:** Did you look at how fast any project was growing, or a trending list, when choosing something? When was the last time?

**Sam:** Trending lists, no, I don't use them. I'm. actually kind of allergic to that. Stars on skill repos are meaningless. A lot of these repos are weeks old and being pushed on Twitter and Reddit.

**18. Yue:** Has that burned you, or is it more of a general feeling?

**Sam:** Last year there was a repo, I won't name it, that went from nothing to several thousand stars in a few days. People on my team were excited about it. I was suspicious, and later someone dug in and it came out the stars were bought. Fake accounts. I think there was a writeup somewhere, I don't remember where I saw it. So now if I see a sudden spike I just ignore the number entirely.

**19. Yue:** How did you figure out that spike was suspicious, before the writeup?

**Sam:** It was just. too fast. And the issues were empty. A repo with five thousand stars and zero issues, zero forks to speak of? Real projects get angry people. I couldn't tell you a formula, it just looked off.

**20. Yue:** What did you do after that? About checking things in general?

**Sam:** Nothing structured. I just stopped trusting stars. I look at the contributors and the issues instead. Though, that doesn't scale to skill repos really, because they're so new there's no history to look at. That's the part that's hard. There's no signal. You just read the code, which is fine for me, but I can see most people don't.

**21. Yue:** The last time you recommended a tool to your team, how did you make the case?

**Sam:** Hm. A few weeks ago I suggested we use a different linter plugin, in a code review thread. Short Slack message, basically "this catches the thing we keep missing, here's the config, try it for a week." I don't write big proposals. I showed the config diff and the three bugs it would've caught.

**22. Yue:** What did people push back on?

**Sam:** One of the other seniors asked who maintains it. Which is funny, because that's my line. And someone else said the CI time would go up. I measured it, it was like eight seconds. That was it.

**23. Yue:** Who had the final say?

**Sam:** Our tech lead. He mostly cares whether it breaks the build and whether security signs off. Stars never come up. Never.

**24. Yue:** Did anything go the other way, a tool the team picked and regretted?

**Sam:** The date library, like I said. And a workflow orchestration thing a couple years ago that was hot at the time. Nice demo, impossible to debug in production. We ripped it out after six months.

**25. Yue:** Has stale or out-of-date info ever led you to a wrong choice?

**Sam:** Yeah, blog posts. "Best X in 2022" articles that rank things by popularity, and then you pick the thing and it's dead now. I don't read those anymore. Docs too, sometimes the README says "actively maintained" and the last commit is eighteen months old.

**26. Yue:** Last thing. Is there someone you know who picks tools or skills a lot more often than you, who might be up for a short chat like this?

**Sam:** Maybe. There's a guy on our platform team who evaluates stuff constantly, and a couple of people on the subreddit who post a lot. I'd have to ask them first, I'm not going to just hand out names. Send me something short I can forward, and I'll think about it. No promises. And honestly I'd want to know what you're building before I send anyone anywhere.

**27. Yue:** Totally fair. I'll send a short note. Thanks, this was really helpful.

**Sam:** Sure. Good luck with the class.


---

## Tom

*B4 · Group B · chooses tools for a team*

**1. Yue:** Thanks for doing this. I'm researching how developers choose open-source tools and AI skills. Nothing to sell, just trying to learn. What are you working on right now?

**Tom:** Uh, mostly finals stuff honestly. Nothing coding-heavy this week. I'm doing a data structures problem set and a writing assignment. The group project from last semester is done, so that's off my plate.

**2. Yue:** Tell me about that project. What was it?

**Tom:** It was a web app for the software engineering course. Four of us. A study-group matcher, basically. You put in your classes and it finds people. I was kind of the lead, I guess. Mostly because I made the repo first.

**3. Yue:** Tell me about the last library or tool you added to it. What was it for?

**Tom:** Hmm. Probably Supabase? For auth and the database. And Next.js for the frontend. Those were the main two. We added some Tailwind thing later too, I forget exactly.

**4. Yue:** How did you pick Supabase and Next.js?

**Tom:** Two of my teammates had used them in a class before. Like, the previous semester. So they said "let's just use that" and everyone was fine with it.

**5. Yue:** How did that conversation go? Where did it happen?

**Tom:** Group chat. iMessage, I think. Or maybe Discord. It was like two minutes. Someone said "Next and Supabase?" and we said ok.

**6. Yue:** Did you look at any other options?

**Tom:** Not really. No.

**7. Yue:** What did you look at before deciding? Walk me through what was on your screen.

**Tom:** Nothing, honestly. We didn't look at anything. I think I opened the Supabase page to make sure there was a free tier. That's about it.

**8. Yue:** How long did that take?

**Tom:** Like I said, a couple minutes. Maybe five if you count me checking the free tier.

**9. Yue:** If your teammates hadn't used them before, what would you have done?

**Tom:** I guess we'd have had to figure something out. Probably Googled it? I don't know. It didn't come up.

**10. Yue:** Did you ask any AI about it?

**Tom:** Oh, yeah, once. I asked ChatGPT "best stack for a web app" at some point. It said Next.js and a Postgres thing, I think, so. that's what we already wanted. So that was fine.

**11. Yue:** When was that, relative to the group chat?

**Tom:** After, I think. Or around the same time. I wasn't really using it to decide. Just curious, I guess.

**12. Yue:** Okay. When you brought the stack to the team, how did you make the case?

**Tom:** I didn't really have to. Two people already knew it. It was more like, okay, they know it, we go with it.

**13. Yue:** What did the other two people ask or push back on?

**Tom:** One guy asked if we could use Python for the backend because he liked Flask. But then he'd have to set up a second thing, so we dropped it. That was pretty much it.

**14. Yue:** Did you put anything in writing?

**Tom:** Not really. We had a README with how to run it. I don't think it said why we picked anything.

**15. Yue:** Who had the final say?

**Tom:** Kind of me, since I was leading. But honestly it was whatever the two experienced people said. I wasn't going to fight them on it.

**16. Yue:** What mattered most to you when it was settled?

**Tom:** That nobody had to learn a new thing. We had like ten weeks and a bunch of other classes. If you're learning a new tool you're not building the project.

**17. Yue:** Was there a time where a team picked a tool and regretted it?

**Tom:** Hmm. Not on this one. On an earlier project, a different group, somebody wanted to use some graph database. I forget the name. That was a mess, nobody knew it. We spent like two weeks on setup. But that was the other group, I was just in the class.

**18. Yue:** What was hard about this last project, then?

**Tom:** Honestly, the two other teammates not knowing the tools. They kept getting stuck on Supabase auth and the row-level security stuff. I ended up answering a lot of questions in the chat.

**19. Yue:** What did you do when they got stuck?

**Tom:** Sent them the docs, mostly. Or showed them on a call. One time I just fixed it myself because it was faster.

**20. Yue:** Did anything break or stop being maintained during the project?

**Tom:** Nope. Nothing like that. It was one semester, so I don't think anything would have, you know, died on us.

**21. Yue:** Okay. Switching a bit. Do you use any AI coding tools?

**Tom:** I've got Claude Code installed. I don't use it that much. Mostly Cursor-ish stuff, or just ChatGPT in a browser tab.

**22. Yue:** Have you installed any skills, plugins, rules, or MCP servers for those? Tell me about the last one.

**Tom:** Not skills for Claude Code, no. I did copy a.cursorrules file from a friend once. He sent it to me in a message.

**23. Yue:** What was in it?

**Tom:** I didn't read all of it. Something like "use TypeScript, keep components small." That kind of thing.

**24. Yue:** Did it change anything?

**Tom:** Uh, not that I noticed. I think it kept doing what it was doing. I don't even know if Cursor was picking it up. I never checked.

**25. Yue:** Have you ever gone looking for rules or skills yourself?

**Tom:** No. I guess if someone sent me one I'd try it. Otherwise I wouldn't think to look.

**26. Yue:** When you'd look, where would you go?

**Tom:** Probably GitHub or Google. Or ask my friend. I haven't really needed to.

**27. Yue:** I'm going to skip the rest, you've covered most of it. Last thing: next time you pick a stack, could I watch for ten minutes?

**Tom:** I mean, sure, but it'd be really boring. It's usually just a group chat message. Maybe, like, text me when it happens? I probably won't be starting a new project until next semester though.

**28. Yue:** Okay. Could you introduce me to anyone who picks tools more often than you do?

**Tom:** Hmm. Maybe my friend with the cursorrules? He's always messing with that stuff. I can ask him. No promises though, he's kind of busy.

**29. Yue:** That would be great. Thanks, Tom.

**Tom:** Yeah, no problem. Good luck with it.
