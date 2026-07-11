# Technical Interview Talking Points

*Use this guide to structure your answers when interviewed about AarogyaAgent v2.*

## 1. Tell me about your most complex project.
"I built AarogyaAgent v2, an AI-powered clinical triage system. The core challenge wasn't just connecting an LLM to a frontend, but making it safe for healthcare. I designed a multi-agent system using LangGraph that breaks down triage into specialized steps—Intake, Symptom Analysis, and Diagnosis. I implemented a Confidence-Weighted Reasoning algorithm so that if the AI encounters an ambiguous case, it automatically stops and escalates the task to a physician dashboard I built in Next.js."

## 2. What was the hardest bug you faced?
"Managing state concurrency and testing in async Python. We had a SQLite `database is locked` error causing our integration tests to fail intermittently. It happened because the LangGraph node opened a secondary database session while the pytest fixture held a root transaction. I solved it by injecting a mock factory into `conftest.py` that forced all isolated components to share the test transaction. This eliminated deadlocks and allowed us to achieve a 100% test pass rate."

## 3. How did you handle LLM hallucinations?
"I mitigated hallucinations using two architectural patterns. First, I implemented Retrieval-Augmented Generation (RAG) using ChromaDB, forcing the LLM to ground its differential diagnosis in retrieved medical guidelines. Second, I built hardcoded Python safety validators that intercept the AI's response before it reaches the patient. If the AI detects emergency keywords like 'chest pain', the validator overrides the output and instructs the patient to seek immediate care."

## 4. Why did you choose FastAPI over Express or Django?
"FastAPI was the perfect fit. Healthcare AI requires heavy asynchronous I/O—streaming LLM tokens and vector DB lookups. FastAPI's native `asyncio` support and Pydantic validation meant I could strongly type the API contracts with Next.js, while seamlessly integrating with Python's superior AI ecosystem (LangChain/LangGraph) without bridging two different languages."
