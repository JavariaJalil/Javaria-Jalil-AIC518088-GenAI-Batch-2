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
