# NLP-EDU

This repository contains my bachelor thesis project.

## Setup

Make sure to install every library needed, some of them are described in the requirements.txt file.

You also need to either manually setup a elasticsearch instance, or use the launch_es module by haystack. When setting up manually, make sure to configure the elasticsearch instance correctly. (port, nodes, etc..)

Furthermore you also have to install the haystack library question generation pipeline.
You can find a proper installation guide [here](https://docs.haystack.deepset.ai/docs/installation). Make sure to check for compatibility beforehand.

## Structure

TODO: add project structure description.

## Format

We feed plain text files into the python script, which uses haystack's question generation pipeline, to create questions from a given text. As an example, the following questions are generated from the first lecture note found in clean-data/lecture-data/content_w01.txt

Generated questions:

- What does software engineering involve more than programming?
- What are two types of software products sold on the open market?
- Who builds the software specification?
- What are the four fundamental activities that lead to the production of a software product?
- What are non functional software attributes?
- Why is it usually cheaper in the long run to use software engineering methods and techniques rather than just coding away?
- What type of software is used by different types of devices?
- What is the challenge of building flexible software?
- How is software intertwined with all aspects of our lives?
- Where do stand alone applications run?
- What type of systems focus on personal use?
- Who develops systems for modelling simulation?
- What is a game for a mobile phone called?
- Where is software used to bring entire programs into the cloud?
- What is a computing cloud?
- What do users pay according to how much they use the software?
- The software process includes all of the activities involved in what?
- Software ethics Don't be evil!
- What are the fundamental ideas of software engineering applicable to?
