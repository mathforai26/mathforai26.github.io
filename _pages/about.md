---
layout: page
title: About
nav_order: 2
permalink: /about/
---

# About the course

**CMPUT 654: Mathematical Foundations of Modern AI Systems** is a graduate course taught in Fall 2026.

The organizing question is:

> Where does the power of current AI systems come from, and to what degree do we understand this?

The course begins from the way contemporary systems are actually built: predictive pretraining, large and highly structured datasets, flexible neural representations, gradient-based optimization, supervised and preference-based post-training, and inference-time computation involving memory, search, tools, and verification. We then use simple mathematical models to isolate what each ingredient can provide.

For each apparent obstruction, we will ask three things:

1. Why is the concern reasonable? (Why do things work at all?)
2. Under what structure does a result become nonbinding?
3. What remains unresolved for current systems or otherwise?

The course takes an open minded approach to investigate current approaches to build today's 
undoubtly powerful AI systems.
The course does not assume that present neural approaches will reach every meaningful notion of intelligence,
and is not investigating the philosophical questions of what is even the meaning of intelligence.
Rather, it takes a pragramatic approach of carefully looking at "what went into" building today's systems,
and along the way also asks the questions of what may be missing, including some discussion around
familiar objections against the current main paradigm. 
We will make an effort to distinguish between the epistemic status of various claims.
We will aim for arriving at claims that can be formulated as mathematically precise theorems -- as the
ultimate source of "truth". Some amount of discussion of empirical evidence, plausible explanations, engineering judgments, and open questions will also fit the course.

## Learning goals

By the end of the course, students should be able to:

- explain the main components of the current LLM training and inference recipe;
- use mathematical models to analyze next-token prediction, dependent data, and understand the role and limitations of overparametrization, gradient-based optimization, shared representations, and post-training;
- distinguish representational possibility from learnability, optimization, efficiency, and exact correctness;
- identify the information or computational resource added by interaction, curricula, memory, search, tools, and verifiers;
- read a theorem together with its assumptions and explain which part of a modern AI system it does—and does not—illuminate;
- formulate a precise research question about an unresolved issue at the foundations of modern AI.

## Preparation

Students should be comfortable with multivariable calculus, linear algebra, probability, algorithms, and mathematical proofs. Prior exposure to machine learning is helpful; prior knowledge of transformers is not required.

[Homework 0]({{ '/documents/assignments/assignment0.pdf' | relative_url }}) is an ungraded readiness exercise. It samples the style and prerequisite mathematics of the course. Students should attempt it during the first week and use it to make an honest decision about whether the course is a good fit.
