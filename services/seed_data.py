"""Database Seeding Utility for CampusSkill AI.

Initializes standard skills, job roles, questions, assessments,
and clearly labeled demo accounts for instant evaluation.
"""
from extensions import db
from models.user import User, StudentProfile
from models.skills import Skill, StudentSkill
from models.jobs import JobRole, JobRoleSkill
from models.assessments import Assessment, Question, AssessmentAttempt, AssessmentAnswer
from models.roadmap import Roadmap, RoadmapTask


def seed_database():
    """Populate database with essential domain data and demo accounts."""
    # 1. Seed Skills Catalog
    skills_data = [
        # Programming & Languages
        ("Python", "Programming", "Versatile high-level language for backend, automation, and data."),
        ("Java", "Programming", "Robust object-oriented programming language for enterprise software."),
        ("C", "Programming", "Foundational procedural programming language."),
        ("C++", "Programming", "High-performance systems and competitive programming language."),
        ("JavaScript", "Web Development", "Universal scripting language of the modern web."),
        
        # Web & Frameworks
        ("HTML", "Web Development", "Standard markup language for documents designed to be displayed in a web browser."),
        ("CSS", "Web Development", "Stylesheet language used for describing presentation of HTML documents."),
        ("React", "Web Development", "Component-based declarative frontend library."),
        ("Flask", "Web Development", "Lightweight Python micro-framework for web APIs."),
        ("Node.js", "Web Development", "Server-side JavaScript runtime environment."),
        
        # Databases & Data
        ("SQL", "Database", "Structured query language for relational database management systems."),
        ("Excel", "Data Analysis", "Spreadsheet application for tabular calculations, pivot tables, and charts."),
        ("Power BI", "Data Visualization", "Microsoft business analytics service for interactive dashboards."),
        ("Tableau", "Data Visualization", "Visual analytics platform transforming data into actionable insights."),
        ("Pandas", "Data Analysis", "Python data manipulation and analysis library."),
        ("NumPy", "Data Science", "Python numerical computing library supporting large matrices."),
        ("Machine Learning", "Data Science", "Study of statistical algorithms that learn from data patterns."),
        
        # Core CS & Placement Pillars
        ("Data Structures and Algorithms", "Core CS", "Foundational computer science problem solving structures and asymptotic analysis."),
        ("Operating Systems", "Core CS", "Processes, threads, concurrency, virtual memory, and file systems."),
        ("Computer Networks", "Core CS", "OSI model, TCP/IP, DNS, HTTP/HTTPS, routing protocols."),
        ("Database Management Systems", "Core CS", "ACID transactions, normalization, indexing, and query execution."),
        ("Aptitude", "Aptitude", "Quantitative problem solving, percentages, permutations, and time-distance."),
        ("Logical Reasoning", "Aptitude", "Deductive reasoning, series, syllogisms, and coding-decoding."),
        ("Communication", "Soft Skills", "Verbal presentation, written clarity, and interview communication."),
        ("Problem Solving", "Core CS", "Algorithmic thinking, edge case handling, and analytical troubleshooting.")
    ]

    skill_records = {}
    for name, cat, desc in skills_data:
        skill = Skill.query.filter_by(name=name).first()
        if not skill:
            skill = Skill(name=name, category=cat, description=desc)
            db.session.add(skill)
            db.session.flush()
        skill_records[name] = skill

    # 2. Seed Job Roles & Weighted Requirements
    job_roles_data = [
        {
            "title": "Data Analyst",
            "category": "Data & Analytics",
            "description": "Analyze large datasets, generate business intelligence dashboards, write complex SQL queries, and present data-backed insights to stakeholders.",
            "salary_range": "₹5 LPA - ₹10 LPA (Sample Entry)",
            "skills": [
                ("SQL", 3, "advanced", True, "Master complex window functions, grouping, subqueries, and table joins."),
                ("Excel", 3, "intermediate", True, "Master pivot tables, XLOOKUP, conditional formatting, and chart summaries."),
                ("Power BI", 3, "intermediate", True, "Learn star-schema data modeling, calculated DAX columns, and visual storytelling."),
                ("Python", 2, "intermediate", True, "Practice Pandas, NumPy, data cleaning, and CSV transformations."),
                ("Communication", 2, "intermediate", True, "Practice delivering slide presentations explaining data insights."),
                ("Aptitude", 2, "intermediate", True, "Crucial for clearing company online aptitude screening rounds."),
                ("Tableau", 1, "beginner", False, "Familiarity with Tableau dashboards adds significant competitive edge.")
            ]
        },
        {
            "title": "Software Developer",
            "category": "Software Engineering",
            "description": "Design, build, test, and maintain robust software systems. Requires strong algorithmic problem solving, core computer science, and object-oriented mastery.",
            "salary_range": "₹7 LPA - ₹16 LPA (Sample Entry)",
            "skills": [
                ("Data Structures and Algorithms", 3, "advanced", True, "Essential for clearing technical coding rounds (Arrays, Trees, Graphs, DP)."),
                ("Java", 3, "intermediate", True, "OOP principles, collections framework, multithreading, and memory model."),
                ("SQL", 2, "intermediate", True, "Database schema design, indexing, and relational queries."),
                ("Database Management Systems", 2, "intermediate", True, "ACID properties, transactions, and normalization."),
                ("Operating Systems", 2, "intermediate", True, "Processes, threads, synchronization, deadlocks, and paging."),
                ("Aptitude", 2, "intermediate", True, "General placement screening requirement."),
                ("Problem Solving", 3, "advanced", True, "Strong analytical approach to boundary conditions.")
            ]
        },
        {
            "title": "Frontend Developer",
            "category": "Web Development",
            "description": "Craft responsive, user-friendly, and performant web interfaces using modern HTML, CSS, JavaScript, and frontend frameworks.",
            "salary_range": "₹5.5 LPA - ₹12 LPA (Sample Entry)",
            "skills": [
                ("JavaScript", 3, "advanced", True, "Asynchronous JS, Promises, ES6+, DOM manipulation, and event loop."),
                ("React", 3, "intermediate", True, "State management, Hooks, component lifecycle, and virtual DOM."),
                ("HTML", 3, "advanced", True, "Semantic HTML5, accessibility, SEO best practices."),
                ("CSS", 3, "intermediate", True, "Flexbox, CSS Grid, media queries, and responsive SaaS layouts."),
                ("Communication", 2, "intermediate", True, "Collaborating with designers and product managers.")
            ]
        },
        {
            "title": "Backend Developer",
            "category": "Web Development",
            "description": "Architect scalable server-side systems, RESTful APIs, database transactions, authentication flows, and microservices.",
            "salary_range": "₹7 LPA - ₹15 LPA (Sample Entry)",
            "skills": [
                ("Python", 3, "advanced", True, "Object-oriented Python, decorators, async I/O, and testing."),
                ("Flask", 3, "intermediate", True, "REST APIs, Blueprints, SQLAlchemy ORM, and secure session management."),
                ("SQL", 3, "intermediate", True, "Query optimization, indexing, foreign keys, and migration."),
                ("Computer Networks", 2, "intermediate", True, "HTTP methods, status codes, TCP/IP, and REST architectural constraints."),
                ("Data Structures and Algorithms", 2, "intermediate", True, "Efficient algorithms for high-throughput processing.")
            ]
        },
        {
            "title": "Python Developer",
            "category": "Software Engineering",
            "description": "Develop automation pipelines, web services, and scripts leveraging Python libraries and modular architecture.",
            "salary_range": "₹6 LPA - ₹13 LPA (Sample Entry)",
            "skills": [
                ("Python", 3, "advanced", True, "Deep knowledge of Python standard library, OOP, and data structures."),
                ("Flask", 2, "intermediate", True, "Building backend web services and API endpoints."),
                ("SQL", 2, "intermediate", True, "Relational database operations."),
                ("Data Structures and Algorithms", 2, "intermediate", True, "Algorithmic thinking and time complexity.")
            ]
        },
        {
            "title": "Java Developer",
            "category": "Software Engineering",
            "description": "Build high-throughput, enterprise-grade distributed applications with Java and relational databases.",
            "salary_range": "₹6.5 LPA - ₹14 LPA (Sample Entry)",
            "skills": [
                ("Java", 3, "advanced", True, "Core Java, JVM internals, Collections, Exception handling."),
                ("SQL", 3, "intermediate", True, "Database queries and JDBC/ORM mapping."),
                ("Data Structures and Algorithms", 3, "intermediate", True, "Fundamental algorithmic problem solving."),
                ("Operating Systems", 2, "intermediate", True, "Concurrency, thread pools, and race conditions.")
            ]
        },
        {
            "title": "Business Analyst",
            "category": "Business & Strategy",
            "description": "Bridge the gap between business needs and technological solutions by analyzing metrics, modeling workflows, and communicating requirements.",
            "salary_range": "₹5 LPA - ₹11 LPA (Sample Entry)",
            "skills": [
                ("Excel", 3, "advanced", True, "Advanced formulas, scenarios, financial projections."),
                ("SQL", 2, "intermediate", True, "Data extraction and ad-hoc reporting."),
                ("Power BI", 2, "intermediate", True, "Interactive management reporting dashboards."),
                ("Communication", 3, "advanced", True, "Stakeholder interviews, requirements elicitation, presentations."),
                ("Aptitude", 2, "intermediate", True, "Business logic and quantitative assessments.")
            ]
        },
        {
            "title": "QA Engineer",
            "category": "Quality Assurance",
            "description": "Ensure high software quality through automated test scripts, unit tests, integration testing, and bug tracking.",
            "salary_range": "₹4.5 LPA - ₹9 LPA (Sample Entry)",
            "skills": [
                ("Python", 2, "intermediate", True, "Test automation scripting and assertion libraries."),
                ("SQL", 2, "intermediate", True, "Data verification and database state checking."),
                ("Communication", 2, "intermediate", True, "Documenting test cases, bugs, and edge cases clearly.")
            ]
        },
        {
            "title": "Machine Learning Engineer",
            "category": "Artificial Intelligence",
            "description": "Design and deploy predictive models, neural networks, and feature extraction pipelines using modern ML algorithms.",
            "salary_range": "₹8 LPA - ₹18 LPA (Sample Entry)",
            "skills": [
                ("Python", 3, "advanced", True, "Python programming, vectorization, and model training."),
                ("NumPy", 3, "advanced", True, "Linear algebra and multidimensional array operations."),
                ("Pandas", 3, "advanced", True, "Data exploration, cleaning, aggregation, and feature engineering."),
                ("Machine Learning", 3, "advanced", True, "Supervised & unsupervised learning, cross-validation, hyperparameter tuning."),
                ("SQL", 2, "intermediate", True, "Feature store and training dataset queries."),
                ("Data Structures and Algorithms", 2, "intermediate", True, "Asymptotic efficiency of model scoring.")
            ]
        }
    ]

    for role_data in job_roles_data:
        role = JobRole.query.filter_by(title=role_data["title"]).first()
        if not role:
            role = JobRole(
                title=role_data["title"],
                category=role_data["category"],
                description=role_data["description"],
                salary_range=role_data["salary_range"]
            )
            db.session.add(role)
            db.session.flush()

        for s_name, weight, min_lvl, req, tip in role_data["skills"]:
            skill_obj = skill_records.get(s_name)
            if skill_obj:
                existing_rs = JobRoleSkill.query.filter_by(job_role_id=role.id, skill_id=skill_obj.id).first()
                if not existing_rs:
                    rs = JobRoleSkill(
                        job_role_id=role.id,
                        skill_id=skill_obj.id,
                        importance_weight=weight,
                        min_proficiency=min_lvl,
                        is_required=req,
                        recommendation_tip=tip
                    )
                    db.session.add(rs)

    # 3. Seed Assessments & Practice Question Bank
    assessments_data = [
        {
            "title": "SQL Querying & Database Fundamentals",
            "category": "SQL",
            "description": "Assess your understanding of relational joins, aggregate functions, subqueries, grouping, and primary/foreign keys.",
            "duration": 15,
            "passing": 60.0,
            "questions": [
                {
                    "text": "Which SQL clause is used to filter groups created by the GROUP BY clause?",
                    "a": "WHERE", "b": "HAVING", "c": "ORDER BY", "d": "LIMIT",
                    "correct": "B",
                    "expl": "HAVING filters aggregate groups, whereas WHERE filters individual rows before grouping."
                },
                {
                    "text": "What type of JOIN returns all records from the left table and matched records from the right table?",
                    "a": "INNER JOIN", "b": "RIGHT JOIN", "c": "LEFT JOIN", "d": "FULL OUTER JOIN",
                    "correct": "C",
                    "expl": "LEFT JOIN (or LEFT OUTER JOIN) preserves all rows from the left table, placing NULLs where the right table has no match."
                },
                {
                    "text": "Which SQL aggregate function computes the total number of non-null values in a specified column?",
                    "a": "SUM()", "b": "COUNT()", "c": "TOTAL()", "d": "AVG()",
                    "correct": "B",
                    "expl": "COUNT(column) returns the number of non-null entries in that column."
                },
                {
                    "text": "What is the primary purpose of an index on a database table?",
                    "a": "Enforce data encryption",
                    "b": "Speed up data retrieval operations",
                    "c": "Reduce physical disk space",
                    "d": "Prevent duplicate entries always",
                    "correct": "B",
                    "expl": "Indexes provide fast lookup paths (like B-trees) to dramatically accelerate SELECT query performance."
                },
                {
                    "text": "Which constraint ensures that all values in a column are distinct across the table?",
                    "a": "CHECK", "b": "DEFAULT", "c": "UNIQUE", "d": "FOREIGN KEY",
                    "correct": "C",
                    "expl": "The UNIQUE constraint ensures every row has a distinct non-null value for that column."
                }
            ]
        },
        {
            "title": "Python Programming & Data Structures",
            "category": "Python",
            "description": "Evaluate core Python knowledge including mutable vs immutable types, list comprehensions, decorators, and dictionaries.",
            "duration": 15,
            "passing": 60.0,
            "questions": [
                {
                    "text": "Which of the following data structures in Python is immutable?",
                    "a": "List", "b": "Dictionary", "c": "Set", "d": "Tuple",
                    "correct": "D",
                    "expl": "Tuples are immutable sequences in Python; their elements cannot be modified after instantiation."
                },
                {
                    "text": "What is the time complexity of searching for an element in a Python dictionary by key on average?",
                    "a": "O(1)", "b": "O(log n)", "c": "O(n)", "d": "O(n^2)",
                    "correct": "A",
                    "expl": "Python dictionaries are implemented using hash tables, giving average O(1) key lookup complexity."
                },
                {
                    "text": "What does the 'yield' keyword in Python do when used inside a function?",
                    "a": "Terminates the function permanently",
                    "b": "Turns the function into a generator",
                    "c": "Raises a runtime exception",
                    "d": "Spawns a background thread",
                    "correct": "B",
                    "expl": "The 'yield' statement suspends execution and returns a generator iterator producing values lazily on demand."
                },
                {
                    "text": "Which built-in Python module is used for interacting with regular expressions?",
                    "a": "regex_py", "b": "re", "c": "string", "d": "match",
                    "correct": "B",
                    "expl": "The standard library module 're' provides regular expression matching operations in Python."
                },
                {
                    "text": "What does a list comprehension [x**2 for x in range(4)] produce?",
                    "a": "[0, 1, 4, 9]", "b": "[1, 4, 9, 16]", "c": "[0, 2, 4, 6]", "d": "(0, 1, 4, 9)",
                    "correct": "A",
                    "expl": "range(4) yields 0, 1, 2, 3. Squaring each results in [0, 1, 4, 9]."
                }
            ]
        },
        {
            "title": "Quantitative & Logical Aptitude",
            "category": "Aptitude",
            "description": "Test speed and accuracy on percentages, ratios, probability, series, and analytical problem solving.",
            "duration": 15,
            "passing": 60.0,
            "questions": [
                {
                    "text": "A train 150m long passes a pole in 15 seconds. What is the speed of the train in km/h?",
                    "a": "30 km/h", "b": "36 km/h", "c": "40 km/h", "d": "45 km/h",
                    "correct": "B",
                    "expl": "Speed = Distance / Time = 150 / 15 = 10 m/s. In km/h: 10 * (18 / 5) = 36 km/h."
                },
                {
                    "text": "If a product is sold at a 20% profit for ₹600, what was its cost price?",
                    "a": "₹480", "b": "₹500", "c": "₹520", "d": "₹550",
                    "correct": "B",
                    "expl": "Selling Price = Cost Price * 1.20 => Cost Price = 600 / 1.2 = ₹500."
                },
                {
                    "text": "Find the missing number in the sequence: 2, 6, 12, 20, 30, ?",
                    "a": "40", "b": "42", "c": "44", "d": "48",
                    "correct": "B",
                    "expl": "Differences are +4, +6, +8, +10, so next difference is +12 => 30 + 12 = 42 (also n*(n+1))."
                },
                {
                    "text": "Two dice are thrown simultaneously. What is the probability of getting a sum of 7?",
                    "a": "1/6", "b": "1/12", "c": "5/36", "d": "7/36",
                    "correct": "A",
                    "expl": "Pairs giving 7: (1,6),(2,5),(3,4),(4,3),(5,2),(6,1) = 6 pairs out of 36 => 6/36 = 1/6."
                },
                {
                    "text": "A can finish a task in 10 days, B in 15 days. Working together, how many days will they take?",
                    "a": "5 days", "b": "6 days", "c": "7 days", "d": "8 days",
                    "correct": "B",
                    "expl": "Combined 1 day work = 1/10 + 1/15 = 5/30 = 1/6. Thus, 6 days."
                }
            ]
        },
        {
            "title": "Data Structures & Algorithms (DSA)",
            "category": "DSA",
            "description": "Essential placement coding interview questions on time complexity, recursion, trees, sorting, and stacks.",
            "duration": 15,
            "passing": 60.0,
            "questions": [
                {
                    "text": "What is the worst-case time complexity of QuickSort?",
                    "a": "O(n log n)", "b": "O(n)", "c": "O(n^2)", "d": "O(log n)",
                    "correct": "C",
                    "expl": "When pivot selection produces completely unbalanced partitions (e.g. already sorted array with first element as pivot), QuickSort degrades to O(n^2)."
                },
                {
                    "text": "Which data structure follows the Last-In-First-Out (LIFO) principle?",
                    "a": "Queue", "b": "Stack", "c": "Linked List", "d": "Heap",
                    "correct": "B",
                    "expl": "A Stack operates on a LIFO discipline where elements are pushed and popped from the top."
                },
                {
                    "text": "What is the maximum number of children a node can have in a Binary Tree?",
                    "a": "1", "b": "2", "c": "3", "d": "Unlimited",
                    "correct": "B",
                    "expl": "By definition, each node in a binary tree has at most two children (left and right)."
                },
                {
                    "text": "Which algorithm is optimal for finding the shortest path in an unweighted graph?",
                    "a": "Depth First Search (DFS)",
                    "b": "Breadth First Search (BFS)",
                    "c": "Bellman-Ford",
                    "d": "Kruskal's Algorithm",
                    "correct": "B",
                    "expl": "BFS visits nodes level by level, guaranteeing the shortest path in unweighted graphs in O(V + E) time."
                },
                {
                    "text": "What is the space complexity of an in-place merge sort implementation?",
                    "a": "O(1)", "b": "O(log n)", "c": "O(n)", "d": "O(n^2)",
                    "correct": "A",
                    "expl": "True in-place sorting algorithms use O(1) auxiliary space beyond variables for index pointers."
                }
            ]
        },
        {
            "title": "Professional Communication & HR Interview Prep",
            "category": "Communication",
            "description": "Evaluate professional email etiquette, STAR interview method, and workplace communication concepts.",
            "duration": 10,
            "passing": 60.0,
            "questions": [
                {
                    "text": "What does the STAR framework stand for in competency-based job interviews?",
                    "a": "Story, Theme, Argument, Result",
                    "b": "Situation, Task, Action, Result",
                    "c": "Skill, Target, Ability, Review",
                    "d": "Strategy, Team, Analysis, Resolution",
                    "correct": "B",
                    "expl": "STAR stands for Situation, Task, Action, Result — the universally accepted behavioral interview framework."
                },
                {
                    "text": "When answering 'What is your greatest weakness?', what is the most professional approach?",
                    "a": "Claim you have no weaknesses",
                    "b": "Share a critical flaw that disqualifies you for the position",
                    "c": "Mention a real area for growth along with specific proactive steps you take to improve it",
                    "d": "Use a cliché like 'I am too much of a perfectionist'",
                    "correct": "C",
                    "expl": "Recruiters look for genuine self-awareness and demonstrable commitment to continuous learning."
                },
                {
                    "text": "In professional email communication, what is the best use of the BCC field?",
                    "a": "To hide all recipients when sending an announcement to protect privacy",
                    "b": "To criticize a colleague privately",
                    "c": "To ensure everyone replies to all",
                    "d": "To attach large file documents",
                    "correct": "A",
                    "expl": "Blind Carbon Copy (BCC) hides recipient email addresses from each other, protecting recipient privacy on bulk notices."
                }
            ]
        }
    ]

    for a_data in assessments_data:
        test = Assessment.query.filter_by(title=a_data["title"]).first()
        if not test:
            test = Assessment(
                title=a_data["title"],
                category=a_data["category"],
                description=a_data["description"],
                duration_minutes=a_data["duration"],
                passing_score=a_data["passing"]
            )
            db.session.add(test)
            db.session.flush()

        for q_data in a_data["questions"]:
            q_exists = Question.query.filter_by(assessment_id=test.id, question_text=q_data["text"]).first()
            if not q_exists:
                q = Question(
                    assessment_id=test.id,
                    question_text=q_data["text"],
                    option_a=q_data["a"],
                    option_b=q_data["b"],
                    option_c=q_data["c"],
                    option_d=q_data["d"],
                    correct_option=q_data["correct"],
                    explanation=q_data["expl"]
                )
                db.session.add(q)

    # 4. Seed Demo Users for Evaluation
    # Admin User
    admin = User.query.filter_by(email="admin@campusskill.edu").first()
    if not admin:
        admin = User(email="admin@campusskill.edu", role="admin")
        admin.set_password("Admin@123")
        db.session.add(admin)

    # Placement Officer User
    po = User.query.filter_by(email="placement@campusskill.edu").first()
    if not po:
        po = User(email="placement@campusskill.edu", role="placement_officer")
        po.set_password("Placement@123")
        db.session.add(po)

    # Main Demo Student
    student_user = User.query.filter_by(email="student@campusskill.edu").first()
    if not student_user:
        student_user = User(email="student@campusskill.edu", role="student")
        student_user.set_password("Student@123")
        db.session.add(student_user)
        db.session.flush()

        # Find target role: Data Analyst
        da_role = JobRole.query.filter_by(title="Data Analyst").first()

        profile = StudentProfile(
            user_id=student_user.id,
            full_name="Rahul Sharma (Demo Student)",
            college_name="National Engineering College",
            branch="Computer Science",
            current_year="3rd Year",
            graduation_year=2026,
            career_objective="Aspiring Data Analyst skilled in Python, SQL, and database systems aiming for high-impact placement opportunities.",
            target_job_role_id=da_role.id if da_role else None,
            github_url="https://github.com/rahul-sharma-demo",
            linkedin_url="https://linkedin.com/in/rahul-sharma-demo",
        )
        db.session.add(profile)
        db.session.flush()

        # Add initial student skills (Python=intermediate, SQL=beginner, Excel=intermediate, Communication=beginner)
        initial_skills = [
            ("Python", "intermediate"),
            ("SQL", "beginner"),
            ("Excel", "intermediate"),
            ("Communication", "beginner"),
            ("HTML", "intermediate")
        ]
        for s_n, lvl in initial_skills:
            sk = skill_records.get(s_n)
            if sk:
                db.session.add(StudentSkill(
                    student_profile_id=profile.id,
                    skill_id=sk.id,
                    proficiency_level=lvl,
                    verified=False
                ))

    # Additional Demo Students for Placement Officer analytics dashboard
    additional_students = [
        ("priya.patel@campusskill.edu", "Priya Patel", "Information Technology", "4th Year", "Software Developer", [("Java", "advanced"), ("SQL", "intermediate"), ("Data Structures and Algorithms", "advanced")]),
        ("amit.verma@campusskill.edu", "Amit Verma", "Computer Science", "3rd Year", "Frontend Developer", [("JavaScript", "advanced"), ("React", "intermediate"), ("HTML", "advanced"), ("CSS", "advanced")]),
        ("sneha.rao@campusskill.edu", "Sneha Rao", "Electronics & Comm", "4th Year", "Data Analyst", [("Python", "intermediate"), ("Excel", "advanced"), ("SQL", "intermediate"), ("Power BI", "intermediate")]),
        ("vikram.singh@campusskill.edu", "Vikram Singh", "Mechanical Eng", "3rd Year", "Python Developer", [("Python", "beginner"), ("SQL", "beginner")])
    ]

    for email, name, branch, yr, role_name, skills_tuple in additional_students:
        u = User.query.filter_by(email=email).first()
        if not u:
            u = User(email=email, role="student")
            u.set_password("Student@123")
            db.session.add(u)
            db.session.flush()

            target_r = JobRole.query.filter_by(title=role_name).first()
            p = StudentProfile(
                user_id=u.id,
                full_name=f"{name} (Demo)",
                college_name="National Engineering College",
                branch=branch,
                current_year=yr,
                graduation_year=2026,
                career_objective=f"Focused on placement opportunities as a {role_name}.",
                target_job_role_id=target_r.id if target_r else None
            )
            db.session.add(p)
            db.session.flush()

            for s_n, lvl in skills_tuple:
                sk = skill_records.get(s_n)
                if sk:
                    db.session.add(StudentSkill(
                        student_profile_id=p.id,
                        skill_id=sk.id,
                        proficiency_level=lvl
                    ))

    db.session.commit()
