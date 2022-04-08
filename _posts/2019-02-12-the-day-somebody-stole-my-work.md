---
title: The day somebody "stole" my work
author: Lucas A. Meyer
date: '2019-02-12'
slug: the-day-somebody-stole-my-work
categories:
  - Data Science
  - Workplace
tags:
  - Data Science
  - Workplace
image:
  caption: ''
  focal_point: ''
---

Part of the work of data science is to create machines that people can use to solve problems. Sometimes these machines can be re-used for other problems with little need for reconfiguration. Sometimes the people reusing one of the machines a data scientist creates will do so without letting the data scientist know until there's a problem.

To protect the innocent, some details of the stories below have been changed.

## The chatbot

Years ago, I wrote a chatbot to automate some really mundane question-answering for my team. Although it was not something extremely high-tech, it was the exact right tool for the job. Most chatbots I've seen are "Rube Goldberg machines", like the "Self Operating Napkin" below. My chatbot really cut down on mundane manual work, and therefore was really successful.

![Rube Goldberg Self-Operating Napkin](https://upload.wikimedia.org/wikipedia/commons/a/a9/Rube_Goldberg%27s_%22Self-Operating_Napkin%22_%28cropped%29.gif)

Because of its success, my chatbot got a lot of use and it started to be shown to customers as an example of our usage of technology. "Some guy in some place", let's call him G, became a specialist in demonstrating the chatbot I wrote, and he would do so very well. 

After a while, somebody had a question about my chatbot in an internal distribution list. The question went like "Can that chatbot do X?". I answered that "No, it can't do that - that was something that I had thought about but ended up never implementing it". In a monumental display of corporate civility, someone replied over me saying: "You should ask G, as he is the creator of that chatbot". I actually declined to further the discussion, and to my knowledge everybody on that thread still thinks that G is the creator of the chatbot. 

![chatbot](chatbot.png)

That made me realize that G was not putting a lot of effort in attributing my work.

## The recommendation system

At some point I wrote a recommendation system to solve a specific problem, let's call it the "X Recommender". It was not particularly well written but it did the job: it recommended X with a decent precision. However, by the time I was done, the client (let's call them C) that needed that problem solved was moved out. I made a note to improve on that system at some point and stashed it. 

A few years later, someone wanted to be mentored by me, and they happened to be a specialist in X. So we started building models around X, and at some point we revived the "X Recommender" to make it better. 

![Recommendation System](rec.png)

At this point, people from C came back asking for an "X Recommender", and they also wanted to learn how to build one. I told them how to build one, step-by-step. They did not succeed in building it for production, but built it enough for a presentation and scheduled time for us to work together to make it ready for production. 

Meanwhile, I presented the very old "X recommender" to a group. A member of the group saw the similarities and asked me why I was taking credit for the work that C had done.

That made me realize that C was not putting a lot of effort in attributing my work.

## The consequences of not having the work attributed

It's not like I'm not [recognized](https://treasurytoday.com/adam-smith-awards-yearbook/adam-smith-awards-yearbook-2017) for my work, quite the opposite. I think the downside is more "societal", or "corporate-wide". In some sense, this is like a [signalling problem](https://en.wikipedia.org/wiki/Signalling_(economics)) in which a non-expert in a particular work product signals that they're an expert. If the signal is misinterpreted, problems that the expert could solve may end up being directed to the non-expert, and that may result in solvable problems not being solved.

There are upsides, however. One upside is that a lot of trivial problems and issues gets filtered from the expert and solved by the non-expert instead. Another upside is that the non-expert will likely get better over time, if only to maintain the façade. Presumably the gain in skills from the non-expert will be faster than for the expert, so overall the skills for the company overall will increase.

## I actually don't have an answer

I'm not sure how to make this better. I have received feedback that I don't "sell" my work enough, but it's a complicated equation...

![Complicated math](math.gif)

The problem is that selling the work takes time, and that will sometimes result in less time to do high-quality data science work. It may also result in wider than optimal adoption, which will require extra support, also detracting to high-quality data science work. Perhaps it pays better, but higher-quality also generally pays better than lower-quality, so it's not that simple.

Of course, I wish my work was such high-quality that this was the real problem. The likely explanation is that I rather work with models than sell them.
