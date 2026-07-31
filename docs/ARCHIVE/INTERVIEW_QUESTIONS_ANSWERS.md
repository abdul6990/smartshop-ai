# HACKWITHINFY INTERVIEW — MOCK QUESTIONS & ANSWERS
## Specialist Programmer Role at Infosys

---

## 🎯 BEHAVIORAL QUESTIONS

### Q: Tell me about yourself

**ANSWER:**
```
"Hi, I'm Syed Abdul Rehaman, a third-year Computer Science student 
at SASTRA University with a CGPA of 9.09.

My passion is building AI-powered applications that solve real problems. 
My major project is SmartShop AI — an end-to-end price intelligence platform 
that helps online shoppers find genuine deals across Amazon, Flipkart, 
and Meesho.

I built this using LangGraph to orchestrate 5 AI agents working together:
a Product Finder, Price Historian, Market Analyzer, AI Predictor, 
and Alert Manager. The standout feature is a deal-signal engine that 
classifies prices as GENUINE_BARGAIN or FAKE_DISCOUNT.

Beyond projects, I have research experience in deep learning, achieving 
94% accuracy on hyperspectral image classification from IEEE research.

I'm excited about the Specialist Programmer role at Infosys because I want 
to build scalable solutions that impact millions of users."
```

---

### Q: Why do you want to join Infosys?

**ANSWER:**
```
"I want to join Infosys for three reasons:

1. Scale: Infosys serves Fortune 500 clients worldwide. I want to work 
   on systems that impact millions of users.

2. Innovation: Infosys has strong focus on AI and automation. Their 
   Lex platform and automation initiatives align with my interest 
   in agentic AI.

3. Growth: The Specialist Programmer track offers structured learning 
   with real project exposure. I want to learn from experienced 
   engineers while contributing from day one.

HackWithInfy is the perfect opportunity to showcase my problem-solving 
skills and join this community."
```

---

### Q: What are your strengths?

**ANSWER:**
```
"My three key strengths are:

1. Full-Stack Problem Solving: I can take a problem from idea to 
   deployment. My SmartShop AI project demonstrates end-to-end 
   development - from architecture design to user-facing features.

2. AI/ML Implementation: I don't just use pre-trained models. I 
   understand the underlying algorithms and can implement research 
   papers, like my hyperspectral classification project.

3. Quick Learning: I'm comfortable picking up new technologies. 
   When I needed WhatsApp alerts, I learned Twilio API in a day. 
   When scraping failed, I learned cloudscraper library.

These skills make me effective in a fast-paced environment."
```

---

### Q: What are your weaknesses?

**ANSWER:**
```
"One area I'm working on is over-engineering.

Sometimes I add features or abstractions that aren't necessary for 
the current scope. For example, in SmartShop AI, I initially built 
a complex caching system when a simple in-memory cache would suffice.

I've learned to scope features based on MVP first, then add complexity 
only when justified by real needs. I now ask myself: "Is this needed 
for the user story, or am I adding it for 'just in case'?"
```

---

### Q: How do you handle pressure?

**ANSWER:**
```
"I handle pressure in three ways:

1. Break it down: When facing a complex problem, I break it into 
   smaller tasks. This makes it manageable and provides quick wins.

2. Prioritize: I use Eisenhower matrix - urgent + important first.
   Everything else can wait.

3. Take breaks: When stuck, I step away for 10 minutes. Often the 
   solution comes when I return with fresh perspective.

For example, during HackWithInfy preparation, I had college exams 
and project deadlines. I scheduled dedicated hours for each, avoided 
multitasking, and asked professors for deadline extensions when needed."
```

---

## 💻 TECHNICAL QUESTIONS (DSA)

### Q: Explain your approach to problem-solving

**ANSWER:**
```
"My approach:
1. Understand the problem - Read twice, note constraints
2. Plan - Think of brute force first, then optimize
3. Code - Clean, commented, with edge cases handled
4. Test - Dry run with examples, including edge cases
5. Optimize - Time and space complexity analysis

Example: For array problems, I first ask:
- Can I sort? (O(n log n) vs O(n) solution?)
- Do I need hash map for O(1) lookup?
- Is two-pointer or sliding window applicable?"
```

---

### Q: Difference between array and linked list

| Aspect | Array | Linked List |
|--------|-------|-------------|
| Access | O(1) random | O(n) sequential |
| Insert | O(n) | O(1) at head |
| Memory | Contiguous | Scattered |
| Size | Fixed | Dynamic |

---

### Q: What is polymorphism in OOP?

```
Polymorphism means "many forms". Two types:

1. Compile-time (Overloading):
   Same function name, different parameters
   e.g., print(int), print(string), print(float)

2. Runtime (Overriding):
   Child class redefines parent's method
   e.g., Animal.speak() vs Dog.speak()
```

---

### Q: Explain REST API

```
REST = Representational State Transfer

Key principles:
- Stateless: Each request has all info
- Client-Server: Separate concerns
- Cacheable: Responses can be cached
- Uniform Interface: Standard endpoints

HTTP methods:
- GET: Read resource
- POST: Create resource
- PUT: Update resource
- DELETE: Remove resource

Example: GET /api/users returns all users
         GET /api/users/123 returns user with ID 123
```

---

## 🐍 PYTHON QUESTIONS

### Q: What is the difference between list and tuple?

| Aspect | List | Tuple |
|--------|------|-------|
| Mutable | Yes | No |
| Syntax | [] | () |
| Performance | Slower | Faster |
| Use | Dynamic data | Fixed data |

---

### Q: What is GIL in Python?

```
Global Interpreter Lock

- Only one thread executes Python bytecode at a time
- Makes Python single-threaded for CPU-bound tasks
- BUT I/O operations can happen in parallel

For CPU-bound tasks: Use multiprocessing
For I/O-bound tasks: Use threading or asyncio
```

---

### Q: What are decorators?

```python
# Decorator adds functionality to existing function
def my_decorator(func):
    def wrapper():
        print("Before")
        func()
        print("After")
    return wrapper

@my_decorator
def say_hello():
    print("Hello!")

# Equivalent to: say_hello = my_decorator(say_hello)
```

---

## 🤖 AI/ML QUESTIONS

### Q: What is the difference between AI, ML, and DL?

```
AI: Artificial Intelligence - Making machines smart (broad)
ML: Machine Learning - Machines learn from data (subset of AI)
DL: Deep Learning - Neural networks with multiple layers (subset of ML)
```

---

### Q: What is overfitting?

```
Overfitting: Model memorizes training data, fails on new data

Signs:
- Training accuracy >> Validation accuracy
- Complex model fitting noise

Solutions:
1. More training data
2. Simpler model (fewer parameters)
3. Regularization (L1, L2, Dropout)
4. Cross-validation
```

---

### Q: Explain CNN

```
Convolutional Neural Network for images

Layers:
1. Conv: Extract features (filters)
2. Pool: Reduce size (max pooling)
3. Flatten: Convert to 1D
4. Dense: Classification layers

Key insight: Learns filters automatically!
(Traditional ML requires manual feature extraction)
```

---

### Q: What is attention mechanism?

```
Attention allows model to focus on relevant parts

In Transformer:
- Q (Query): What am I looking for?
- K (Key): What do I contain?
- V (Value): Actual content

Attention Score = softmax(Q @ K.T / √d) @ V

Used in:
- NLP (translation, summarization)
- Image classification
- Object detection (DETR)
```

---

## 🌐 PROJECT-SPECIFIC QUESTIONS

### Q: How does your SmartShop AI handle anti-bot protection?

```
"I implemented a multi-layer strategy:

1. cloudscraper library to bypass Cloudflare
2. Realistic browser headers (User-Agent, Accept-Language)
3. Exponential backoff retry (5 seconds, then 10, then 20)
4. Fallback to Tavily Search API for data

This taught me the importance of graceful degradation."
```

---

### Q: Why did you use LangGraph over simple function calls?

```
"LangGraph provides:

1. State management between agents
2. Visual graph representation (easier to debug)
3. Error handling per node
4. Can parallelize independent tasks
5. Easy to add/modify agents

For simple pipelines, function calls suffice. But for multi-agent 
systems with shared state and complex dependencies, LangGraph 
provides better organization and reliability."
```

---

### Q: How does your deal-signal algorithm work?

```
"The algorithm uses deterministic rules:

GENUINE_BARGAIN:
- Current price < 90% of average price
- AND current price ≤ 30-day lowest

FAKE_DISCOUNT:
- Previous day price was inflated (>120% of average)
- AND current price dropped >10% from previous day

This is better than ML because:
1. Explainable - I can tell users WHY it's a deal
2. Fast - No training required
3. Reliable - No model errors
```

---

### Q: How would you scale your price tracking system?

```
"To scale, I would:

1. Database: Use PostgreSQL with indexing
   - Index on product_id, last_checked
   - Partition by time (monthly)

2. Caching: Redis for hot data
   - Cache prices for 5 minutes
   - Cache user sessions

3. Async Processing:
   - Use Celery + Redis for background tasks
   - Price check every hour, not real-time

4. Load Balancing:
   - Multiple API instances
   - Round-robin or least connections

5. Microservices:
   - Separate: Scraper, API, Notifier
   - Scale independently
```

---

## 📋 CODING CHALLENGE PREP

### Must-Know Topics:

| Topic | Difficulty | Frequency |
|-------|-----------|----------|
| Arrays/Strings | Easy | Very High |
| Two Pointers | Easy | High |
| Sliding Window | Easy-Medium | High |
| Hash Maps | Easy | Very High |
| Binary Search | Medium | High |
| Linked Lists | Medium | Medium |
| Trees | Medium | Medium |
| Dynamic Programming | Medium-Hard | High |
| Graphs | Hard | Medium |
| Tries | Hard | Low |

### Top 20 LeetCode Problems to Solve:

```
Easy:
1. Two Sum
2. Valid Parentheses
3. Reverse Linked List
4. Merge Two Sorted Lists
5. Best Time to Buy Stock
6. Contains Duplicate
7. Palindrome Number

Medium:
8. Longest Substring Without Repeat
9. Longest Palindromic Substring
10. Container With Most Water
11. Binary Tree Zigzag Level Order
12. Coin Change
13. Word Search
14. Number of Islands
15. Course Schedule

Hard:
16. Merge k Sorted Lists
17. LRU Cache
18. Serialize/Deserialize BST
```

---

## 🎯 LAST-MINUTE TIPS

1. **Practice on paper** - Interviews might not have IDE
2. **Speak while coding** - Explain your thought process
3. **Start simple** - Brute force first, optimize later
4. **Ask clarifying questions** - Before jumping to solution
5. **Test edge cases** - Empty, single, duplicate, negative
6. **Be confident** - You got this far, you can do it!