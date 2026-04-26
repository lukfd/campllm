# Final Project Proposal

# Introduction

**Camp LLM** By *Luca Comba*

I am really interested in Large Language Models and other Conversational AI applications. At the same time I am founding it to be very difficult to pick a topic or an idea for the Final Project of this class. The main reason that has been burdensome, was because I am not able to find a project idea that can be both helpful for my community and not too time consuming to implement.

These are some of the idea I had:

- A chatbot for searching Minnesota State Parks
- A website that acts as a blue print and a graphic interface for designing AI systems, similar to Figma or LucidChart, but with a pre made list of AI models based on the Arxiv dataset and foundational models [https://info.arxiv.org/help/bulk_data.html](https://info.arxiv.org/help/bulk_data.html) (I was thinking that it might a BERTopic for extracting all possible models and generate a tree for hierarchy of models)
- A website that can function as a tool for visual impared people that can help reading emails and navigate the web

# What

The final project will be focusing on building a **chatbot for searching Minnesota State Parks**. This chatbot will allow users to query information about state parks and receive helpful, conversational responses using a custom-trained language model.

The project scope progresses through three stages:

| Functionality | Minimal Viable Goal | Optimistic Goal |
|---|---|---|
| Data Collection | Batch scraper job to grab content from the web | Comprehensive dataset of all MN parks |
| Language Model | Basic transformer design (Karpathy's GPT) | Train a custom LLM from scratch (Karpathy's nanochat approach) |
| Model Optimization | Basic hyperparameter tuning | Advanced optimization with better data quality |
| User Interface | Command-line chatbot with formatted responses | Interactive website with web interface |
| Deployment | Locally only | Cloud deployment with automated CI/CD |

# Why

I want to learn how to build and train a language model from scratch rather than using pre-built models. Understanding the fundamentals of LLMs through creating a LLM myself might be useful. Second, I want to create a tool that can serve my community and myself. It can be thought as an assistant to help people discover and learn about Minnesota state parks.

# How

## Data Collection

I will scrape Minnesota state parks information from the official DNR website:

- [https://www.dnr.state.mn.us/state_parks/index.html](https://www.dnr.state.mn.us/state_parks/index.html)

The scraper will extract park names, descriptions, amenities, locations, and others.

I might use CloudFlare Crawl [https://developers.cloudflare.com/browser-rendering/](https://developers.cloudflare.com/browser-rendering/)

## Model Development

I will follow Andrej Karpathy's tutorials and repository to build and train my own language model:

- [Karpathy's GPT Tutorial](https://youtu.be/kCc8FmEb1nY)
- [Karpathy's NanoChat](https://github.com/karpathy/nanochat)

These resources provide a solid foundation for building a transformer-based model from scratch and fine-tuning it on my parks dataset.

## Implementation Timeline

1. **Week 1**: Build web scraper and collect park data
2. **Week 2**: Preprocess data and set up model architecture
3. **Week 3**: Train initial model on collected data
4. **Week 4**: Build command-line interface for the chatbot (minimal viable goal)

