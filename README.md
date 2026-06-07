# Agentic Marketing Tool

This is an Agentic Marketing Tool that persuades potential customers by crafting a refined sales pitch. This is a beginner project, that I aim to enhance over time. This tool is designed to help offline businesses establish an online presence. 

## Running this Project

#### Prerequisites
1. Python 3.13
2. uv package manager
3. Firefox browser 
4. geckodriver.exe (included in project root)

#### API Keys
For our project we are using Groq and Mistral AI.
You can apply for keys using these links:
1. [Groq](https://console.groq.com/keys)
2. [MIstral AI](https://admin.mistral.ai/organization/api-keys)

#### Steps to Run:  
1. Locally download this project using this command:

	`git clone https://github.com/JavariaJalil/Javaria-Jalil-AIC518088-GenAI-Batch-2.git`
	Or using UI provided by GitHub.
2. Just run <code> uv sync </code> this will install the required packages to run this project.
3. In your root directory, create a `.env` file and place your Mistral and Groq API Keys in these variables.
	<pre> MISTRAL_API_KEY="Your API Key"</pre>
	<pre> GROQ_API="Your API Key"</pre>
4. Now to run the project use this command:<code> uv run agentic_tool.py</code>

## Working and Functionality

This tool can take commands related to marketing in natural language. Currently it can generate a refined sales pitch related to a business, then pitch the customer using their WhatsApp contact.

### How it helps our business:

For example we are a web development services software house and we want to pitch our web development services to a potential customer. This is how we can ask this tool to do it, when it asks to enter your query we can enter something like this(keywords, business niche, business name and phone number with country code are required.)

<blockquote>Hi! business name is Ahmed Photography, keywords are pictures, wedding_shoot, modeling_shoot, niche is fashion, phone_number is 92----------.</blockquote> 

It takes keywords related to the customer's business and then creates sales pitch, it keeps on recreating the sales pitch until the sales pitch is reasonable and ensures that the created pitch talks about the user's business briefly but more importantly how our business services can improve their business i.e. enhance their sales, create an online store using best software practices etc.

### What is an agentic tool?

An agentic tool is a software system powered by Large Language Models where the LLM output controls the workflow rather than hardcoded logic. Agents are LLMs assigned to accomplish a specific task and can be supplemented with tools, structured outputs, and the ability to hand off work to other agents. This architecture involves multiple LLM calls, orchestration through tools, and a planner coordinating activities across an environment where LLMs interact with each other — with autonomy being the core essence that separates agentic AI from traditional automation.

### Functionality:

This project uses a **Supervisor Agent** as the central coordinator. It receives the user's request, checks whether all business details are available, and if not, calls the `get_business_details` tool to collect the business name, niche, and keywords before proceeding.

Once the details are ready, the Supervisor delegates to the **Sales Pitch Agent**, which first generates a pitch using the `create_sales_pitch` tool, then immediately evaluates it using `rate_score_pitch`. If the score is below 7, the pitch is sent back for regeneration — this loop can repeat up to a maximum number of 6 times until the pitch meets the quality threshold.

The approved pitch is then handed off to the **Communication Agent**, which passes the phone number and pitch text to the `send_sms` tool, which delivers the message directly to the customer on WhatsApp.

