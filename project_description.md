
# Project: Orchids SWE Internship Take-Home – Website Cloning

## 🌐 Overview

This project is a take-home challenge for the **Software Engineering Internship at Orchids**. It aims to simulate one of Orchids' core AI features: **Website Cloning**. The goal is to build a minimal end-to-end web application that:

1. Accepts a public website URL as input.
2. Scrapes the design and content of the website.
3. Uses an LLM (Large Language Model) to replicate that website in HTML.
4. Returns a preview of the cloned website that looks as aesthetically similar as possible.

---

## 📁 Folder Structure

```
.
├── README.md                # Instructions and setup guide
├── project.md               # Project overview and scope (this file)
├── frontend/                # Next.js + TypeScript web application
└── backend/                 # Python + FastAPI backend server
```

---

## 🛠 Tech Stack

* **Frontend**: Next.js (React) + TypeScript
* **Backend**: Python + FastAPI
* **Optional**: Cloud scraping/browser solutions (e.g., Browserbase, Hyperbrowser)
* **LLM Suggestions**: Claude 4 Sonnet, Gemini 2.5 Pro

---

## 📌 Project Requirements

### 1. Web App

* A user interface where users can:

  * Enter a public website URL.
  * Submit the request.
  * View a **live HTML preview** of the cloned website.

### 2. Website Scraping

* Must extract **useful design context** from the provided URL:

  * DOM structure
  * CSS stylesheets
  * Assets (images, fonts)
  * Screenshots (optional but helpful)
* Should handle:

  * Slow loading websites
  * Websites with IP protection (e.g., firewall, bot detection)
* Performance Tip: Avoid slow local browser scraping in production. Use cloud alternatives if needed.

### 3. LLM Cloning Pipeline

* Design an LLM prompt and architecture to:

  * Accept scraped context (HTML, CSS, screenshots, etc.)
  * Generate high-fidelity HTML clones
* You are encouraged to experiment with:

  * Prompt engineering
  * Chain-of-thought reasoning
  * Agentic workflows

---

## 🔧 Implementation Plan

### Frontend (`frontend/`)

* Input field for URL
* Submit button triggers backend API
* Display area for cloned HTML output (live preview or HTML rendering)

### Backend (`backend/`)

* API Endpoint:

  * Accepts website URL
  * Coordinates scraping and LLM interaction
* Web scraping module

  * Efficiently collects necessary context
* LLM integration module

  * Prepares prompt and sends it to selected LLM
  * Receives HTML output

---

## ✅ Submission Requirements

1. 📦 **Codebase**:

   * Submit a ZIP of your full working project.
   * Ensure your `README.md` contains:

     * Setup steps
     * Any API keys, libraries, or tools required

2. 📹 **Demo Video**:

   * Record a short walkthrough (2–5 minutes)
   * Show:

     * The flow from input → scrape → LLM → output
     * A sample cloning result

---

