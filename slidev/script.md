Slide 1: Cover (15 seconds)

CampLLM is tool we built to make searching Minnesota state parks way easier using Artificial Intelligence. Instead of digging through a bunch of park websites, now you can just ask a question and get answers backed by real park information.

Slide 2: DNR Problem (45 seconds)

The Minnesota Department of Natural Resources website has tons of great information about our state parks, but it's honestly hard to search. The details are spread all over the place. You'll find park hours on one page, trail info buried somewhere else, amenities in another section. And a lot of pages are just really long with boilerplate text mixed in with what you actually care about.

So if you want to know something like 'Which parks near the Twin Cities have camping?' you end up clicking through multiple tabs and scrolling for a while. We thought—why can't we just ask that question and get an instant answer? That's why we built CampLLM.

Slide 3: Why CampLLM (30 seconds)

At its core, CampLLM is a RAG system - a Retrieval-Augmented Generation. It crawls DNR park pages, cleans up the text, splits it into chunks, and stores those chunks in a vector database. So when you ask a question, it finds the most relevant chunks, feeds them to an AI model, and gets back an answer with source links. So you always know where the information came from.

Slide 4: System Pipeline (40 seconds)

On the left side, you see the indexing process. Which is run offline. First, we crawl the DNR pages with Puppeteer, clean the text, chunk it up, embed it using a small efficient model, and store it all in ChromaDB — a vector database built for semantic search.

On the right, when someone asks a question, we retrieve the most relevant chunks, feed them to a language model — we're using Google's Gemini or Gemma — and the model generates an answer grounded in that context.

Slide 5: Chroma + Embeddings (35 seconds)

Now a quick word on the tech. For the embeddings, we use model2vec with a tiny 8-million-parameter model. It's fast and efficient, and it works really well for semantic search on park data.

The database layer is ChromaDB over HTTP. We added bearer token auth so the whole thing can be deployed securely. All of this is abstracted into simple Python classes — an Embedding class handles the vectors, and a Database class wraps the ChromaDB client.

Slide 6: RAG Orchestration (35 seconds)

The RAG class ties everything together. When you ask a question, it queries ChromaDB for the top matching chunks, builds a context block with source metadata, sends that to the LLM with your question, and the model generates an answer. We also parse out which sources got cited in the answer, so we can show you exactly where the info came from.

Slide 8: Web Interface (45 seconds)

We have deployed a web version at campllm.techypond.com. It's a FastAPI backend serving a Vue.js frontend. When you type a question and hit send, the frontend fetches the API, shows a loading indicator while it thinks, then displays the answer with proper markdown formatting and source links.

Slide 9: Results (40 seconds)

From testing, we found some good things: the system does pull relevant park facts accurately, it shows you sources so you can verify, and it can handle questions about amenities, locations, contact info, and more.

Of course, there are limitations too. The quality depends on what's in the dataset—if something isn't scraped from the DNR site, the system won't know about it.  We're also not doing any reranking yet, just straight semantic search.

Slide 10: Future Work (30 seconds)

Going forward, we want to add more data sources like user reviews, photos, and definetly adding geolocation context so that the model knows where parks are located across Minnesota. We want to improve the prompting to get more consistent formatting and have a stronger reranking to boost the most relevant results. Finally we need to handle multi-turn conversations better so chat sessions stay clean.

Slide 11: Thank You (20 seconds)

That's CampLLM. You can try it at campllm.techypond.com, check out the code on GitHub, or reach out to me if you have questions. Thank you!