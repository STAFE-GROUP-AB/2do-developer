# Claude Code Unified Agents Integration

2DO now includes all 48 specialized agents from the [claude-code-unified-agents](https://github.com/stretchcloud/claude-code-unified-agents) repository, providing comprehensive development assistance across all domains.

## 📚 Available Agent Categories

### 🎯 Core Orchestrator (1 agent)
- **orchestrator** - Master coordinator for complex multi-agent workflows

### 💻 Development (14 agents)
- **backend-architect** - API design, microservices, database architecture
- **frontend-specialist** - React, Vue, Angular, modern UI frameworks  
- **python-pro** - Advanced Python, async programming, optimization
- **fullstack-engineer** - End-to-end application development
- **database-specialist** - SQL/NoSQL design, optimization, management
- **mobile-developer** - iOS, Android, React Native, Flutter
- **rust-pro** - Systems programming, memory safety, WebAssembly
- **golang-pro** - Concurrent programming, microservices, cloud-native
- **typescript-pro** - Advanced type systems, large-scale applications
- **javascript-pro** - Modern ES6+, async programming, Node.js
- **java-enterprise** - Spring Boot, microservices, JVM optimization
- **nextjs-pro** - Next.js 14+, App Router, React Server Components
- **react-pro** - Advanced hooks, performance, state management
- **vue-specialist** - Vue 3, Composition API, Nuxt 3, Pinia
- **angular-expert** - Angular 17+, signals, RxJS, enterprise apps

### 🏗️ Infrastructure (7 agents)
- **devops-engineer** - CI/CD, containerization, Kubernetes, automation
- **cloud-architect** - AWS, GCP, Azure architecture and optimization
- **incident-responder** - Production debugging, log analysis, recovery
- **performance-engineer** - Profiling, optimization, load testing
- **monitoring-specialist** - Observability, metrics, alerting
- **deployment-manager** - Release orchestration, rollback strategies
- **kubernetes-expert** - K8s configuration, helm charts, operators

### ✅ Quality Assurance (6 agents)
- **code-reviewer** - Code quality, security, best practices review
- **security-auditor** - Vulnerability assessment, penetration testing
- **test-engineer** - Test automation, strategies, frameworks
- **e2e-test-specialist** - Playwright, Cypress, test strategies
- **performance-tester** - Load testing, stress testing, benchmarking
- **accessibility-auditor** - WCAG compliance, screen reader testing

### 🤖 Data & AI (6 agents)
- **ai-engineer** - LLMs, computer vision, NLP, ML systems
- **data-engineer** - ETL pipelines, data warehouses, big data
- **data-scientist** - Statistical analysis, ML models, visualization
- **mlops-engineer** - ML pipelines, experiment tracking, deployment
- **prompt-engineer** - LLM optimization, RAG systems, fine-tuning
- **analytics-engineer** - dbt, data modeling, BI tools

### 💼 Business & Process (6 agents)
- **project-manager** - Agile, sprint planning, team coordination
- **product-strategist** - Market analysis, roadmapping, metrics
- **business-analyst** - Business process optimization, gap analysis, ROI
- **technical-writer** - Technical documentation, API docs, guides
- **requirements-analyst** - Requirements engineering, user stories, traceability
- **api-designer** - OpenAPI/GraphQL specs, REST design, SDK generation

### 🎨 Creative (1 agent)
- **ux-designer** - User experience, wireframing, design systems

### 🔮 Specialized Domains (7 agents)
- **blockchain-developer** - Smart contracts, Web3, DeFi
- **mobile-developer** - iOS, Android, React Native, Flutter
- **game-developer** - Unity, Unreal Engine 5, Godot 4, procedural generation
- **embedded-engineer** - Arduino, Raspberry Pi, STM32, real-time systems
- **fintech-specialist** - Payment systems, PCI DSS compliance, fraud detection
- **healthcare-dev** - HIPAA/FHIR compliance, EHR systems, medical device integration
- **ecommerce-expert** - Shopping carts, checkout optimization, inventory management

## 🚀 Usage

The agents are available through Claude Code's sub-agent system. You can:

1. **Use interactive selection**: `@agents` command to browse and select
2. **Auto-selection**: Claude automatically chooses the best agent
3. **Direct invocation**: `@agent-name` for specific agents
4. **Orchestrated workflows**: `@orchestrator` for complex tasks

## Examples

```bash
# Direct agent usage
@python-pro optimize this async function
@frontend-specialist create React dashboard
@devops-engineer setup CI/CD pipeline

# Orchestrated workflow
@orchestrator build complete e-commerce platform
```

## Benefits

- **54 Total Agents**: Comprehensive coverage across all technical domains
- **Production-Ready**: Each agent includes extensive expertise and examples
- **Specialized Knowledge**: Deep domain expertise in specific areas
- **Flexible Integration**: Works seamlessly with existing 2DO features
- **Multi-Agent Workflows**: Complex tasks handled by coordinated teams

---

*All agents are located in `.claude/agents/` and follow Claude Code sub-agent specifications.*