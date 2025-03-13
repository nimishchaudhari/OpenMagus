# OpenMagus Output Flow

## Request-Response Flow
```mermaid
sequenceDiagram
    participant U as User
    participant API as API Layer
    participant C as Coordinator
    participant P as Planner
    participant K as Knowledge
    participant E as Executor
    participant M as Memory Systems
    participant L as LiteLLM
    participant T as Tools

    U->>API: Submit Request
    API->>C: Forward Request
    
    rect rgb(200, 220, 255)
        note right of C: Planning Phase
        C->>P: Request Task Planning
        P->>K: Request Context
        K->>M: Query Memory
        M->>K: Return Context
        K->>P: Provide Context
        P->>L: Generate Plan
        L->>P: Return Plan
        P->>C: Return Task Plan
    end
    
    rect rgb(255, 220, 200)
        note right of C: Execution Phase
        C->>E: Execute Tasks
        E->>T: Use Required Tools
        T->>E: Tool Results
        E->>M: Store Results
        E->>C: Execution Status
    end
    
    rect rgb(220, 255, 200)
        note right of C: Response Phase
        C->>K: Request Response Format
        K->>L: Generate Response
        L->>K: Formatted Response
        K->>C: Final Response
        C->>API: Return Response
        API->>U: Present Result
    end
```

## Data Flow Architecture
```mermaid
flowchart TD
    subgraph Input[Input Processing]
        UR[User Request]
        API[API Layer]
        Val[Input Validation]
    end
    
    subgraph Processing[Core Processing]
        direction TB
        
        subgraph Planning[Planning Phase]
            TP[Task Planning]
            CP[Context Processing]
            PG[Plan Generation]
        end
        
        subgraph Execution[Execution Phase]
            TE[Task Execution]
            TM[Tool Management]
            EM[Error Management]
        end
        
        subgraph Memory[Memory Operations]
            ES[Episodic Storage]
            SS[Semantic Storage]
            PS[Procedural Storage]
        end
    end
    
    subgraph Output[Output Generation]
        RG[Response Generation]
        RF[Response Formatting]
        QC[Quality Control]
    end
    
    subgraph Feedback[Feedback Loop]
        PM[Performance Monitoring]
        RL[Result Logging]
        OS[Output Storage]
    end
    
    UR --> API --> Val
    Val --> TP
    
    TP --> CP --> PG
    PG --> TE --> TM
    
    TE --> EM
    EM --> |Error| TP
    EM --> |Success| RG
    
    CP -.-> ES
    TE -.-> SS
    PG -.-> PS
    
    RG --> RF --> QC
    QC --> |Fail| RG
    QC --> |Pass| OS
    
    OS --> PM --> RL
    RL -.-> Memory
    
    style Input fill:#f9f,stroke:#333,stroke-width:2px
    style Processing fill:#bbf,stroke:#333,stroke-width:2px
    style Output fill:#bfb,stroke:#333,stroke-width:2px
    style Feedback fill:#fbf,stroke:#333,stroke-width:2px
```

# User Interface & Output Methods

## 1. Command Line Interface (CLI)
```mermaid
graph TD
    CLI[CLI Interface] --> Commands[Command Parser]
    Commands --> |Interactive Mode| REPL[REPL Loop]
    Commands --> |Batch Mode| Batch[Batch Processing]
    
    REPL --> Output[Output Handler]
    Batch --> Output
    
    Output --> |Real-time| Stream[Streaming Output]
    Output --> |Completion| Final[Final Result]
    Output --> |Error| Error[Error Messages]
    
    Stream --> Progress[Progress Updates]
    Stream --> Interim[Interim Results]
    
    subgraph Display Formats
        Progress --> Term[Terminal UI]
        Interim --> Term
        Final --> |Plain Text| Text[Text Output]
        Final --> |Rich Format| Rich[Rich Output]
        Error --> Term
    end
```

### Features:
- Interactive REPL mode for step-by-step interaction
- Batch processing mode for script-based automation
- Real-time progress updates with spinners/progress bars
- Rich terminal output (colors, formatting, tables)
- Command history and auto-completion
- Error handling with detailed feedback

## 2. REST API Interface
```mermaid
graph LR
    API[REST API] --> Sync[Synchronous]
    API --> Async[Asynchronous]
    
    Sync --> |Immediate| Direct[Direct Response]
    Async --> |Long-running| Status[Status Endpoint]
    
    Direct --> JSON[JSON Response]
    Status --> WS[WebSocket Updates]
    Status --> Poll[Polling Endpoint]
    
    subgraph Response Types
        JSON --> Results[Task Results]
        JSON --> Meta[Metadata]
        WS --> Progress[Progress Updates]
        WS --> Stream[Streaming Results]
        Poll --> State[Task State]
    end
```

### Features:
- RESTful endpoints for all operations
- Synchronous endpoints for quick operations
- Asynchronous endpoints for long-running tasks
- WebSocket support for real-time updates
- Structured JSON responses
- Authentication and rate limiting
- Detailed error responses with status codes

## 3. Python SDK
```mermaid
graph TD
    SDK[Python SDK] --> Sync[Synchronous Client]
    SDK --> Async[Async Client]
    
    Sync --> Methods[Method Calls]
    Async --> Promise[Promise-based Calls]
    
    Methods --> Objects[Python Objects]
    Promise --> Objects
    
    subgraph Integration Options
        Objects --> Direct[Direct Use]
        Objects --> Event[Event Handlers]
        Objects --> Stream[Stream Processors]
    end
```

### Features:
- Clean, Pythonic interface
- Both synchronous and asynchronous APIs
- Type hints for better IDE support
- Event-driven programming support
- Streaming response handlers
- Automatic retries and error handling
- Comprehensive documentation

## 4. Web Dashboard
```mermaid
graph TD
    Web[Web Dashboard] --> Real[Real-time View]
    Web --> History[History View]
    Web --> Config[Configuration]
    
    Real --> Status[Status Monitor]
    Real --> Live[Live Output]
    
    History --> Tasks[Task History]
    History --> Logs[System Logs]
    
    Config --> Settings[System Settings]
    Config --> Tools[Tool Management]
    
    subgraph Visualization
        Status --> Metrics[Performance Metrics]
        Live --> Stream[Output Stream]
        Tasks --> Timeline[Task Timeline]
        Logs --> Search[Log Search]
    end
```

### Features:
- Real-time task monitoring
- Interactive task management
- System configuration interface
- Performance metrics visualization
- Log viewing and searching
- Tool configuration management
- User authentication and authorization

## Output Format Standards
1. **Structured Data**
   - JSON/YAML for machine consumption
   - Structured error messages
   - Metadata inclusion
   - Versioned response formats

2. **Human-Readable Output**
   - Formatted text with proper indentation
   - Color-coded output for different types
   - Progress indicators
   - Interactive elements
   - Markdown support for rich text

3. **Multi-Modal Output**
   - Text responses
   - Generated images
   - Code snippets with syntax highlighting
   - Data visualizations
   - File downloads
