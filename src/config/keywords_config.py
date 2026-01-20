"""
Keyword Configuration for Deterministic Analysis Engine

This file contains all keyword mappings used by the analysis engine to classify
GitHub repositories into domains, detect frameworks, and identify specializations.

HOW TO MODIFY:
1. Add new keywords to existing categories by appending to the lists
2. Create new categories by adding new dictionary entries
3. Keywords are case-insensitive (automatically lowercased during matching)
4. Use specific keywords to avoid false positives (e.g., "react" not "re")

MATCHING LOGIC:
- Keywords are matched against: repo description + topics
- Short keywords (< 4 chars) use word boundary matching
- Longer keywords use substring matching
"""

# ============================================================================
# DOMAIN CLASSIFICATION KEYWORDS
# ============================================================================
# These keywords determine the PRIMARY and SECONDARY business domains
# of a developer's work (e.g., E-commerce, Healthcare, AI, etc.)

DOMAIN_KEYWORDS = {
    # ----- COMMERCE & RETAIL -----
    "E-commerce": [
        "shop", "store", "cart", "payment", "checkout", "stripe", "paypal", 
        "commerce", "inventory", "order", "magento", "shopify", "woocommerce", 
        "pos", "billing", "merchant", "catalog", "product"
    ],
    
    # ----- HEALTHCARE & MEDICAL -----
    "Healthcare": [
        "health", "medical", "doctor", "patient", "clinic", "hospital", "bio", 
        "pharmacy", "appointment", "ehr", "emr", "telemedicine", "hl7", "dicom", 
        "fhir", "diagnosis", "prescription", "healthcare"
    ],
    
    # ----- FINANCE & BANKING -----
    "Finance (FinTech)": [
        "finance", "stock", "trade", "crypto", "bitcoin", "wallet", "invoice", 
        "bank", "ledger", "transaction", "defi", "nft", "blockchain", "forex", 
        "trading", "quant", "accounting", "fintech", "payment gateway"
    ],
    
    # ----- EDUCATION -----
    "Education (EdTech)": [
        "learn", "course", "school", "student", "class", "exam", "quiz", "edu", 
        "lms", "university", "elearning", "teacher", "curriculum", "grade", 
        "edtech", "mooc", "training"
    ],
    
    # ----- MARKETING & GROWTH -----
    "Marketing & SEO": [
        "marketing", "seo", "analytics", "ads", "campaign", "crm", "content", 
        "social", "traffic", "conversion", "funnel", "landing page", "email", 
        "newsletter", "sitemap", "crawler", "growth", "adwords", "sem"
    ],
    
    # ----- ARTIFICIAL INTELLIGENCE & MACHINE LEARNING -----
    "AI & Machine Learning": [
        # Core ML/AI
        "machine learning", "ml", "ai", "artificial intelligence", "deep learning",
        "neural network", "neural", "model training", "inference", "prediction",
        
        # ML Frameworks
        "tensorflow", "pytorch", "keras", "scikit-learn", "scikit", "sklearn",
        "xgboost", "lightgbm", "catboost", "gradient boosting",
        
        # Deep Learning Architectures
        "cnn", "rnn", "lstm", "gru", "transformer", "attention", "bert", "gpt",
        "gan", "generative", "autoencoder", "resnet", "vgg", "inception",
        
        # AI Agents & LLMs
        "langchain", "langgraph", "autogpt", "agent", "autonomous", "rag",
        "llm", "large language model", "chatbot", "conversational ai",
        "openai", "anthropic", "gemini", "ollama", "huggingface",
        
        # MLOps & Deployment
        "mlflow", "wandb", "tensorboard", "mlops", "model deployment",
        "model serving", "kubeflow", "sagemaker",
        
        # General AI
        "reinforcement learning", "supervised", "unsupervised", "semi-supervised",
        "feature engineering", "hyperparameter", "optimization", "ensemble"
    ],
    
    # ----- COMPUTER VISION -----
    "Computer Vision": [
        "computer vision", "vision", "opencv", "image processing", "cv2",
        "object detection", "yolo", "detectron", "mask rcnn", "faster rcnn",
        "image classification", "image recognition", "facial recognition",
        "segmentation", "semantic segmentation", "instance segmentation",
        "pose estimation", "tracking", "ocr", "optical character recognition",
        "image generation", "stable diffusion", "dall-e", "midjourney",
        "video analysis", "video processing", "frame extraction"
    ],
    
    # ----- NATURAL LANGUAGE PROCESSING -----
    "Natural Language Processing": [
        "nlp", "natural language processing", "text analysis", "text mining",
        "sentiment analysis", "text classification", "named entity recognition",
        "ner", "tokenization", "lemmatization", "stemming", "pos tagging",
        "spacy", "nltk", "word2vec", "glove", "embeddings", "word embeddings",
        "language model", "text generation", "summarization", "translation",
        "question answering", "information extraction", "topic modeling",
        "semantic search", "vector search", "sentence transformers"
    ],
    
    # ----- DATA SCIENCE & ANALYTICS -----
    "Data Science & Analytics": [
        "data science", "data analysis", "analytics", "statistical analysis",
        "pandas", "numpy", "scipy", "matplotlib", "seaborn", "plotly",
        "visualization", "data visualization", "dashboard", "tableau",
        "jupyter", "notebook", "ipynb", "kaggle", "data exploration",
        "exploratory data analysis", "eda", "statistical modeling",
        "time series", "forecasting", "regression", "classification",
        "clustering", "dimensionality reduction", "pca", "t-sne"
    ],
    
    # ----- DATA ENGINEERING -----
    "Data Engineering": [
        "data engineering", "etl", "data pipeline", "data warehouse",
        "data lake", "big data", "hadoop", "spark", "pyspark", "kafka",
        "airflow", "data processing", "batch processing", "stream processing",
        "data integration", "data transformation", "data quality",
        "snowflake", "redshift", "bigquery", "databricks", "dbt",
        "data modeling", "data architecture", "data orchestration"
    ],
    
    # ----- INFRASTRUCTURE & CLOUD -----
    "DevOps & Cloud": [
        "docker", "kubernetes", "aws", "cloud", "deploy", "server", "ci/cd", 
        "pipeline", "terraform", "ansible", "monitor", "log", "scale", 
        "microservice", "serverless", "devops", "infrastructure", "container"
    ],
    
    # ----- SECURITY -----
    "Cybersecurity": [
        "security", "hack", "penetration", "exploit", "cryptography", "auth", "oauth", 
        "jwt", "vulnerability", "malware", "firewall", "ids", "ips", "cve", 
        "audit", "encryption", "ssl", "tls"
    ],
    
    # ----- BLOCKCHAIN & WEB3 -----
    "Blockchain & Web3": [
        "blockchain", "smart contract", "solidity", "ethereum", "web3", "token", 
        "dapp", "ipfs", "consensus", "wallet", "mint", "dao", "polygon", "nft"
    ],
    
    # ----- IOT & HARDWARE -----
    "IoT & Embedded": [
        "iot", "embedded", "arduino", "raspberry", "sensor", "firmware", "mqtt", 
        "esp32", "robotics", "driver", "hardware", "microcontroller"
    ],
    
    # ----- GAMING -----
    "Game Development": [
        "game", "unity", "unreal", "godot", "sprite", "physics", "render", 
        "shader", "multiplayer", "fps", "rpg", "engine", "gaming"
    ],
    
    # ----- WEB DEVELOPMENT -----
    "Web Development": [
        "web app", "web application", "website builder", "cms", 
        "fullstack", "full-stack", "full stack", "mern", "mean", "lamp",
        "jamstack", "static site", "server-side rendering", "ssr"
    ],
    
    # ----- UI/UX DESIGN -----
    "UI/UX Design": [
        "ui design", "ux design", "user interface", "user experience",
        "figma", "sketch", "adobe xd", "prototyping", "wireframe",
        "design system", "component library", "accessibility", "responsive design",
        "frontend design", "visual design", "interaction design"
    ],
    
    # ----- FRONTEND DEVELOPMENT -----
    "Frontend Development": [
        "frontend", "front-end", "spa", "single page application",
        "pwa", "progressive web app", "client-side", "browser",
        "dom manipulation", "responsive", "cross-browser"
    ],
    
    # ----- BACKEND DEVELOPMENT -----
    "Backend Development": [
        "backend", "back-end", "api development", "api endpoint",
        "rest api", "graphql api", "microservices", "backend service",
        "database design", "authentication", "authorization", "backend logic"
    ],
    
    # ----- MOBILE -----
    "Mobile Development": [
        "mobile", "ios", "android", "flutter", "react native", "app", "swift", 
        "kotlin", "tablet", "mobile app"
    ],
    
    # ----- ENTERPRISE -----
    "Enterprise Software": [
        "erp", "crm", "hrm", "enterprise", "business", "saas", "b2b", "workflow", 
        "management", "salesforce", "sap", "oracle"
    ],
    
    # ----- MEDIA & CONTENT -----
    "Media & Entertainment": [
        "video", "streaming", "media", "audio", "podcast", "music", "player", 
        "youtube", "netflix", "twitch", "content"
    ],
    
    
    # ----- SOCIAL & COMMUNICATION -----
    "Social & Communication": [
        "social", "chat", "messaging", "forum", "community", "slack", "discord", 
        "telegram", "whatsapp", "notification"
    ],
    
    # ----- TRADITIONAL INDUSTRIES (For Job Matching) -----
    "Civil Engineering & Construction": [
        "civil engineering", "construction", "structural", "infrastructure",
        "building", "architecture", "cad", "autocad", "bim", "engineering",
        "surveying", "contractor", "project management", "site management",
        "concrete", "steel", "bridge", "road", "highway"
    ],
    
    "Architecture & Design": [
        "architecture", "architectural", "interior design", "3d modeling",
        "rendering", "autocad", "revit", "sketchup", "blueprint", "floor plan",
        "building design", "urban planning", "landscape", "spatial design"
    ],
    
    "Accounting & Auditing": [
        "accounting", "bookkeeping", "audit", "financial reporting", "tax",
        "payroll", "invoice", "expense", "ledger", "balance sheet",
        "quickbooks", "accounting software", "financial analysis", "compliance",
        "gaap", "ifrs", "tax filing", "accounts payable", "accounts receivable"
    ],
    
    "Legal & Compliance": [
        "legal", "law", "compliance", "regulatory", "contract", "legal tech",
        "case management", "document management", "litigation", "paralegal",
        "legal research", "court", "lawyer", "attorney", "gdpr", "privacy law"
    ],
    
    "Real Estate & Property": [
        "real estate", "property", "rental", "lease", "landlord", "tenant",
        "property management", "mls", "listing", "broker", "realtor",
        "real estate crm", "property listing", "housing", "apartment"
    ],
    
    "Manufacturing & Supply Chain": [
        "manufacturing", "supply chain", "inventory", "warehouse", "logistics",
        "production", "quality control", "erp", "mrp", "plm", "scm",
        "factory", "assembly", "procurement", "vendor management"
    ],
    
    "Logistics & Transportation": [
        "logistics", "transportation", "shipping", "delivery", "freight",
        "fleet", "tracking", "route optimization", "warehouse", "distribution",
        "courier", "last mile", "supply chain", "tms"
    ],
    
    "Hospitality & Tourism": [
        "hotel", "hospitality", "tourism", "booking", "reservation",
        "restaurant", "travel", "accommodation", "guest", "pms",
        "hotel management", "travel agency", "tour", "vacation"
    ],
    
    "Agriculture & Food Tech": [
        "agriculture", "farming", "agritech", "crop", "livestock",
        "farm management", "precision agriculture", "food tech", "food safety",
        "agricultural", "harvest", "irrigation", "soil"
    ],
    
    "Energy & Utilities": [
        "energy", "power", "utility", "electricity", "solar", "renewable",
        "grid", "smart grid", "energy management", "utilities", "water",
        "gas", "oil", "energy efficiency", "meter", "billing"
    ],
    
    "Telecommunications": [
        "telecom", "telecommunications", "network", "5g", "broadband",
        "voip", "telephony", "carrier", "mobile network", "isp",
        "network infrastructure", "cellular"
    ],
    
    "Media & Publishing": [
        "media", "publishing", "journalism", "news", "magazine", "newspaper",
        "content publishing", "digital media", "broadcast", "press",
        "editorial", "print", "online publishing"
    ],
    
    "Human Resources & Recruitment": [
        "hr", "human resources", "recruitment", "hiring", "applicant tracking",
        "ats", "hrms", "talent", "onboarding", "payroll", "employee",
        "job board", "recruiting", "benefits", "performance management"
    ],
    
    "Consulting & Professional Services": [
        "consulting", "professional services", "advisory", "strategy",
        "management consulting", "business consulting", "project management",
        "client management", "service delivery"
    ],
    
    "Insurance & Risk Management": [
        "insurance", "insurtech", "policy", "claims", "underwriting",
        "risk management", "actuarial", "premium", "coverage", "broker",
        "insurance management", "claims processing"
    ],
    
    "Retail & Point of Sale": [
        "retail", "pos", "point of sale", "store", "shop", "inventory",
        "cash register", "barcode", "scanner", "retail management",
        "merchandising", "stocktaking"
    ],
    
    "Non-Profit & NGO": [
        "non-profit", "nonprofit", "ngo", "charity", "donation", "fundraising",
        "volunteer", "social impact", "humanitarian", "philanthropy",
        "grant management", "donor management"
    ]
}


# ============================================================================
# DOMAIN WEIGHTS FOR PRIORITIZATION
# ============================================================================
# Weights determine priority when multiple domains match
# Higher weight = higher priority in classification

DOMAIN_WEIGHTS = {
    # AI/ML domains get highest priority (2.0x)
    "AI & Machine Learning": 2.0,
    "Computer Vision": 2.0,
    "Natural Language Processing": 2.0,
    "Data Science & Analytics": 2.0,
    "Data Engineering": 2.0,
    
    # Specialized technical domains (1.5x)
    "Blockchain & Web3": 1.5,
    "IoT & Embedded": 1.5,
    "Game Development": 1.5,
    "Cybersecurity": 1.5,
    "DevOps & Cloud": 1.5,
    
    # Business domains (1.3x)
    "Finance (FinTech)": 1.3,
    "Healthcare": 1.3,
    "E-commerce": 1.3,
    "Education (EdTech)": 1.3,
    "Enterprise Software": 1.3,
    
    # Traditional industries (1.2x)
    "Civil Engineering & Construction": 1.2,
    "Architecture & Design": 1.2,
    "Accounting & Auditing": 1.2,
    "Legal & Compliance": 1.2,
    "Real Estate & Property": 1.2,
    "Manufacturing & Supply Chain": 1.2,
    "Logistics & Transportation": 1.2,
    "Insurance & Risk Management": 1.2,
    
    # Service industries (1.0x - baseline)
    "Hospitality & Tourism": 1.0,
    "Agriculture & Food Tech": 1.0,
    "Energy & Utilities": 1.0,
    "Telecommunications": 1.0,
    "Media & Publishing": 1.0,
    "Human Resources & Recruitment": 1.0,
    "Consulting & Professional Services": 1.0,
    "Retail & Point of Sale": 1.0,
    "Non-Profit & NGO": 1.0,
    
    # Development domains (1.0x - baseline)
    "Mobile Development": 1.0,
    "Frontend Development": 1.0,
    "Backend Development": 1.0,
    "Web Development": 0.8,  # Lower priority to avoid over-matching
    "UI/UX Design": 1.0,
    
    # General domains (0.8x)
    "Marketing & SEO": 0.8,
    "Media & Entertainment": 0.8,
    "Social & Communication": 0.8
}


# ============================================================================
# TECHNOLOGY KEYWORDS (Frameworks, Libraries, Tools)
# ============================================================================
# These keywords are categorized by type for better skill classification
# Each detected keyword will be tagged with its category in the final report

TECH_KW_CATEGORIES = {
    
    # -------------------------------------------------------------------------
    # AI, LLM & AGENT FRAMEWORKS
    # -------------------------------------------------------------------------
    "AI & Agents": [
        # LLM Orchestration
        "langchain", "langgraph", "llamaindex", "semantic kernel",
        
        # No-Code AI
        "flowise", "n8n", "langflow", "dify",
        
        # Agent Frameworks
        "autogpt", "babyagi", "crewai", "superagi", "agentgpt",
        
        # LLM Providers
        "openai", "anthropic", "gemini", "mistral", "ollama", "cohere",
        
        # ML Libraries
        "huggingface", "transformers", "sentence-transformers",
        
        # Vector Databases
        "pinecone", "chromadb", "weaviate", "milvus", "qdrant", "faiss",
        
        # RAG & Embeddings
        "rag", "embeddings", "vector search"
    ],
    
    # -------------------------------------------------------------------------
    # BACKEND FRAMEWORKS
    # -------------------------------------------------------------------------
    "Backend Framework": [
        # Node.js / JavaScript
        "nest.js", "nestjs", "nest", "@nestjs/core", "@nestjs/common",
        "express", "expressjs", "express.js", "fastify", "koa", "koajs", "hapi", "hapijs",
        "node.js", "nodejs", "sails", "sailsjs", "feathers", "feathersjs",
        "adonis", "adonisjs", "loopback", "restify",
        
        # Python
        "django", "flask", "fastapi", "tornado", "litestar", "sanic", "aiohttp",
        "pyramid", "bottle", "falcon", "cherrypy", "web2py", "turbogears",
        "starlette", "quart",
        
        # Java/JVM
        "spring boot", "spring", "springboot", "jakarta", "micronaut", "quarkus", 
        "vert.x", "vertx", "play", "playframework", "dropwizard", "spark java",
        "grails", "struts", "vaadin",
        
        # Go
        "gin", "gin-gonic", "echo", "fiber", "chi", "beego", "revel", "iris",
        "gorilla", "buffalo", "goji",
        
        # PHP
        "laravel", "symfony", "codeigniter", "slim", "lumen", "yii", "yii2",
        "cakephp", "zend", "phalcon", "fuelphp",
        
        # Ruby
        "rails", "ruby on rails", "sinatra", "hanami", "grape", "roda", "padrino",
        "camping",
        
        # .NET / C#
        "asp.net", "aspnet", "dotnet", "blazor", ".net core", "nancy", "servicestack",
        
        # Rust
        "actix", "actix-web", "rocket", "axum", "warp", "tide",
        
        # Others
        "graphql", "apollo", "apollo-server", "grpc", "grpc-web",
        "rest api", "restful", "websocket", "socket.io", "socketio",
        "trpc", "t3-stack"
    ],
    
    # -------------------------------------------------------------------------
    # FRONTEND FRAMEWORKS
    # -------------------------------------------------------------------------
    "Frontend Framework": [
        # Modern Frameworks
        "react", "reactjs", "react.js", "vue", "vuejs", "vue.js", "angular", 
        "angularjs", "svelte", "sveltekit", "preact", "solidjs", "solid-js", 
        "qwik", "alpine.js", "alpinejs",
        
        # Component Libraries - React
        "react-dom", "react-router", "react-router-dom", "react-query", "tanstack",
        
        # Component Libraries - Vue
        "vue-router", "vue3", "composition-api",
        
        # Lightweight/Alternative
        "lit", "lit-element", "stencil", "stenciljs", "petite-vue", "hyperapp",
        
        # Legacy (but still important)
        "jquery", "backbone", "backbonejs", "ember", "emberjs", "knockout", "knockoutjs",
        "polymer", "meteor", "meteorjs"
    ],
    
    # -------------------------------------------------------------------------
    # META FRAMEWORKS (Full-stack)
    # -------------------------------------------------------------------------
    "Meta Framework": [
        # React-based
        "next.js", "nextjs", "remix", "gatsby",
        
        # Vue-based
        "nuxt", "nuxt.js", "gridsome",
        
        # Svelte-based
        "sveltekit",
        
        # Multi-framework
        "astro", "fresh", "analog"
    ],
    
    # -------------------------------------------------------------------------
    # MOBILE FRAMEWORKS
    # -------------------------------------------------------------------------
    "Mobile Framework": [
        "react native", "flutter", "expo", "ionic", "cordova", "capacitor", 
        "xamarin", "maui", "nativescript", "tauri"
    ],
    
    # -------------------------------------------------------------------------
    # STATE MANAGEMENT
    # -------------------------------------------------------------------------
    "State Management": [
        # React
        "redux", "mobx", "zustand", "recoil", "jotai", "xstate",
        
        # Vue
        "pinia", "vuex",
        
        # Angular
        "ngrx", "akita",
        
        # Other
        "flux", "effector"
    ],
    
    # -------------------------------------------------------------------------
    # CSS FRAMEWORKS & UI LIBRARIES
    # -------------------------------------------------------------------------
    "Styling & UI": [
        # CSS Frameworks
        "tailwind", "tailwindcss", "bootstrap", "bulma", "foundation",
        
        # Component Libraries
        "material ui", "mui", "chakra", "mantine", "shadcn", "daisyui",
        "ant design", "semantic ui",
        
        # CSS-in-JS
        "styled-components", "emotion", "styled-jsx",
        
        # Preprocessors
        "sass", "scss", "less", "stylus", "postcss"
    ],
    
    # -------------------------------------------------------------------------
    # DATABASES
    # -------------------------------------------------------------------------
    "Database": [
        # SQL
        "postgresql", "postgres", "mysql", "mariadb", "sqlite", "mssql",
        
        # NoSQL
        "mongodb", "couchdb", "cassandra", "scylla",
        
        # Key-Value
        "redis", "memcached",
        
        # Graph
        "neo4j", "arangodb", "dgraph",
        
        # Cloud/BaaS
        "dynamodb", "firestore", "firebase", "supabase", "convex", 
        "pocketbase", "appwrite",
        
        # ORMs
        "prisma", "typeorm", "sequelize", "mongoose", "sqlalchemy", "drizzle"
    ],
    
    # -------------------------------------------------------------------------
    # DEVOPS & CLOUD PLATFORMS
    # -------------------------------------------------------------------------
    "DevOps & Cloud": [
        # Containers
        "docker", "podman", "kubernetes", "k8s", "helm", "rancher",
        
        # IaC
        "terraform", "ansible", "pulumi", "cloudformation",
        
        # CI/CD
        "jenkins", "gitlab ci", "github actions", "circleci", "travis ci",
        "azure devops",
        
        # Monitoring
        "prometheus", "grafana", "datadog", "new relic", "splunk", "elk",
        
        # Cloud Providers
        "aws", "azure", "gcp", "google cloud", "digitalocean", "linode",
        
        # Hosting
        "vercel", "netlify", "heroku", "render", "railway", "fly.io"
    ],
    
    # -------------------------------------------------------------------------
    # TESTING FRAMEWORKS
    # -------------------------------------------------------------------------
    "Testing": [
        # JavaScript
        "jest", "mocha", "chai", "jasmine", "vitest", "ava",
        
        # E2E
        "cypress", "playwright", "puppeteer", "selenium", "testcafe",
        
        # Python
        "pytest", "unittest", "nose",
        
        # Java
        "junit", "testng", "mockito",
        
        # Other
        "testing library", "enzyme"
    ],
    
    # -------------------------------------------------------------------------
    # BUILD TOOLS & BUNDLERS
    # -------------------------------------------------------------------------
    "Build Tools": [
        "webpack", "vite", "rollup", "parcel", "esbuild", "turbopack",
        "gulp", "grunt", "npm", "yarn", "pnpm", "bun"
    ],
    
    # -------------------------------------------------------------------------
    # CMS & E-COMMERCE PLATFORMS
    # -------------------------------------------------------------------------
    "CMS & Platforms": [
        # CMS
        "wordpress", "strapi", "contentful", "sanity", "ghost", "drupal",
        
        # E-commerce
        "shopify", "woocommerce", "magento", "prestashop", "bigcommerce"
    ],
    
    # -------------------------------------------------------------------------
    # PAYMENT GATEWAYS
    # -------------------------------------------------------------------------
    "Payment Processing": [
        "stripe", "paypal", "razorpay", "square", "braintree", "paddle",
        "checkout", "adyen"
    ],
    
    # -------------------------------------------------------------------------
    # AUTHENTICATION
    # -------------------------------------------------------------------------
    "Authentication": [
        "auth0", "clerk", "supabase auth", "firebase auth", "okta", "keycloak",
        "passport", "next-auth", "lucia"
    ]
}


# ============================================================================
# FEATURE KEYWORDS (For Job Matching - Common Project Capabilities)
# ============================================================================
# These keywords identify common features and capabilities that projects have
# Useful for matching candidates with jobs requiring specific feature expertise

FEATURE_KEYWORDS = {
    # ----- AUTHENTICATION & SECURITY -----
    "Authentication & Authorization": [
        "authentication", "auth", "login", "signup", "sign up", "register",
        "oauth", "oauth2", "sso", "single sign-on", "jwt", "token",
        "session", "cookie", "authorization", "rbac", "role-based",
        "permission", "access control", "multi-factor", "2fa", "mfa"
    ],
    
    "Security & Encryption": [
        "security", "encryption", "ssl", "tls", "https", "secure",
        "hash", "bcrypt", "crypto", "cryptography", "password",
        "firewall", "csrf", "xss", "sql injection", "sanitization"
    ],
    
    # ----- PAYMENT & COMMERCE -----
    "Payment Processing": [
        "payment", "stripe", "paypal", "checkout", "transaction",
        "billing", "subscription", "invoice", "payment gateway",
        "credit card", "refund", "cart", "shopping cart"
    ],
    
    # ----- REAL-TIME & COMMUNICATION -----
    "Real-time Features": [
        "real-time", "realtime", "live", "websocket", "socket.io",
        "sse", "server-sent events", "push notification", "live chat",
        "live update", "streaming", "real-time sync"
    ],
    
    "Messaging & Chat": [
        "chat", "messaging", "message", "inbox", "conversation",
        "chat room", "direct message", "dm", "group chat"
    ],
    
    "Notifications": [
        "notification", "alert", "push", "email notification",
        "sms", "in-app notification", "toast", "reminder"
    ],
    
    # ----- DATA & ANALYTICS -----
    "Dashboard & Reporting": [
        "dashboard", "report", "reporting", "chart", "graph",
        "visualization", "analytics dashboard", "admin panel",
        "metrics", "kpi", "statistics"
    ],
    
    "Search & Filter": [
        "search", "filter", "advanced search", "full-text search",
        "elasticsearch", "algolia", "autocomplete", "typeahead",
        "faceted search", "query", "sort"
    ],
    
    "Data Import/Export": [
        "import", "export", "csv", "excel", "pdf", "bulk import",
        "data migration", "backup", "download"
    ],
    
    # ----- USER EXPERIENCE -----
    "User Interface": [
        "responsive", "mobile-friendly", "adaptive", "ui", "ux",
        "dark mode", "theme", "responsive design", "mobile-first"
    ],
    
    "Forms & Validation": [
        "form", "validation", "input validation", "form builder",
        "multi-step form", "wizard", "field validation"
    ],
    
    "File Management": [
        "file upload", "upload", "file storage", "image upload",
        "drag and drop", "file preview", "attachment", "media library"
    ],
    
    # ----- INTEGRATION & API -----
    "API & Integration": [
        "api", "rest api", "restful", "graphql", "api endpoint",
        "api integration", "third-party api", "webhook",
        "callback", "api documentation", "swagger", "openapi"
    ],
    
    "Email Integration": [
        "email", "smtp", "sendgrid", "mailgun", "ses",
        "email template", "transactional email", "email campaign"
    ],
    
    # ----- COLLABORATION & SOCIAL -----
    "Collaboration": [
        "collaboration", "team", "multi-user", "sharing", "share",
        "collaborative editing", "co-editing", "workspace"
    ],
    
    "Social Features": [
        "social", "like", "comment", "follow", "share", "feed",
        "activity feed", "news feed", "social login", "profile"
    ],
    
    # ----- CONTENT MANAGEMENT -----
    "Content Management": [
        "cms", "content", "blog", "article", "post", "page",
        "wysiwyg", "editor", "rich text", "markdown",
        "content creation", "publishing"
    ],
    
    "Media Handling": [
        "image", "video", "audio", "media", "gallery",
        "image processing", "thumbnail", "video player",
        "image optimization", "cdn"
    ],
    
    # ----- WORKFLOW & AUTOMATION -----
    "Workflow & Automation": [
        "workflow", "automation", "trigger", "scheduled",
        "cron", "task", "job queue", "background job",
        "pipeline", "process automation"
    ],
    
    "Booking & Scheduling": [
        "booking", "reservation", "appointment", "calendar",
        "schedule", "availability", "time slot", "booking system"
    ],
    
    # ----- INTERNATIONALIZATION -----
    "Localization": [
        "i18n", "internationalization", "localization", "l10n",
        "translation", "multi-language", "multilingual", "locale"
    ],
    
    # ----- PERFORMANCE & SCALABILITY -----
    "Caching & Performance": [
        "cache", "caching", "redis cache", "cdn", "lazy loading",
        "pagination", "infinite scroll", "optimization",
        "performance", "compression"
    ],
    
    # ----- ADMIN & MANAGEMENT -----
    "Admin Features": [
        "admin", "admin panel", "dashboard", "management",
        "settings", "configuration", "user management",
        "role management", "audit log"
    ]
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_all_keywords_flat():
    """
    Returns a flattened dictionary mapping each keyword to its category.
    Used for quick lookups during analysis.
    
    Returns:
        dict: {keyword: category}
    """
    flat_map = {}
    for category, keywords in TECH_KW_CATEGORIES.items():
        for kw in keywords:
            flat_map[kw.lower()] = category
    return flat_map


def get_domain_keywords():
    """Returns the domain classification keywords."""
    return DOMAIN_KEYWORDS


def get_domain_weights():
    """Returns the domain weight multipliers for prioritization."""
    return DOMAIN_WEIGHTS


def get_tech_categories():
    """Returns the technology keyword categories."""
    return TECH_KW_CATEGORIES


def get_feature_keywords():
    """Returns the feature keyword categories."""
    return FEATURE_KEYWORDS
