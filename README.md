# Adrián Salvador Ekomo Mesi Obono

Data & Platform Engineering student (DevOps, DataOps, MLOps) in Leipzig, Germany. Open to internships from December 2026.

[Portfolio](https://adriansalvadorekomodev.vercel.app) · [Notes](https://adriansalvadorekomodev.vercel.app/blog) · [LinkedIn](https://linkedin.com/in/adriansalvadorekomo) · [Email](mailto:adriansalvadorekomo@outlook.com) · CV: [EN](cv/Adrian_Salvador_Ekomo_CV_EN.pdf) · [ES](cv/Adrian_Salvador_Ekomo_CV_ES.pdf) · [FR](cv/Adrian_Salvador_Ekomo_CV_FR.pdf)

I build the platforms data runs on: reproducible infrastructure as code, quality-gated CI/CD and governed data pipelines. I look for the manual, error-prone step where infrastructure, delivery and data meet, and replace it with something that can be reviewed, tested and repeated.

## Selected projects

Ordered by relevance to Data Engineering, Data Platform and DevOps. Each one: the problem, what I did, what changed.

**1. Reconciled $99.4M in revenue through a governed medallion lakehouse**  
<sub>[DataOps Lakehouse](https://github.com/adriansalvadorekomo/DataOps-Lakehouse-for-E-commerce-Analytics)</sub>

- **Problem:** Reports ran ad-hoc queries straight against the operational database, and nothing checked the quality of the data they returned.
- **What I did:** Built a Bronze → Silver → Gold pipeline on Databricks with a fail-fast data-quality gate (nine rules) between Silver and Gold, with the infrastructure in Terraform and pull-request-gated CI.
- **Result:** Revenue reconciles end to end — $99.4M on a synthetic dataset — and a bad batch can no longer reach the Gold marts.
- <sub>Built with Databricks · PySpark · Delta Lake · Terraform · GitHub Actions</sub>

**2. Restored SSH in ~5s with a code-defined bastion failover**  
<sub>[RIF Open edX](https://github.com/adriansalvadorekomo/Stage_ete_RIF_Automatisation)</sub>

- **Problem:** A volunteer organisation of 10+ engineers ran hand-built servers: no infrastructure as code, no automated configuration, no high availability.
- **What I did:** As the DevOps intern, defined the OpenStack infrastructure in Terraform and the server setup as idempotent Ansible roles, shipped a containerised Open edX behind Nginx with HTTPS, and designed a PRIMARY → BACKUP bastion on one Floating IP.
- **Result:** SSH access is restored in about 5 seconds in failover tests, and every infrastructure change is reviewable in Git.
- <sub>Built with OpenStack · Terraform · Ansible · Nginx · Docker</sub>

**3. Killed “works on my machine” with a 10-stage quality-gated pipeline**  
<sub>[PM App CI/CD](https://github.com/adriansalvadorekomo/DevOps-AppGestionDesProjets)</sub>

- **Problem:** A Spring Boot, Angular and MySQL app failed on every handoff: “works on my machine”, no quality check, no container strategy.
- **What I did:** Wrote a 10-stage Jenkins pipeline that fails fast — build, SonarQube analysis, a quality gate that blocks a red release, multistage Docker builds with immutable tags, verified redeploy — then ported the stack to Kubernetes on minikube.
- **Result:** One command takes the app from commit to running containers, and a red quality gate stops the release.
- <sub>Built with Jenkins · SonarQube · Docker · Kubernetes · Spring Boot</sub>

**4. Stopped bad code from ever training a model**  
<sub>[Customer Churn MLOps](https://github.com/adriansalvadorekomo/customer-churn-mlops)</sub>

- **Problem:** A one-off churn notebook: no tests, no schedule, and retraining by hand on the full dataset every time.
- **What I did:** Separated the pipeline logic from the orchestration, blocked every run behind ruff, bandit and six pytest gates, and scheduled three staggered Prefect flows (02:00, 04:00, 06:00 UTC).
- **Result:** Retraining and re-scoring run nightly without overlap, at 85.5% accuracy. Churner recall is 0.42 — documented openly, with class imbalance named as the next fix.
- <sub>Built with Prefect · scikit-learn · ruff · bandit · pytest</sub>

**5. Made a RAG tutor summarise whole chapters, not the five closest passages**  
<sub>[Episteme](https://github.com/adriansalvadorekomo/Episteme)</sub>

- **Problem:** Top-k retrieval reads about 5% of a 30-page chapter, so chapter summaries skip most of it — and a small LLM fills the gaps with fluent guesses.
- **What I did:** Built a course tutor that answers only from its own corpus: a Bronze/Silver lakehouse (object storage plus Iceberg), Graph-RAG retrieval over a kNN knowledge graph, and a study mode that reads a chapter section by section while the answer's structure and citations are laid out in code.
- **Result:** Every answer is cited and carries a sentence-level verification badge. A 16-page chapter is summarised in about 30–45 seconds on a laptop RTX 4060, and a missing diagram is preferred over an invented one.
- <sub>Built with Python · FAISS · Apache Iceberg · FastAPI · Qwen2.5 · uv</sub>

**6. Compared six road-anomaly models on a test set opened exactly once**  
<sub>[RoadAnomaly](https://github.com/adriansalvadorekomo/RoadAnomaly-CRISPDM)</sub>

- **Problem:** A driving camera's segmenter knows a closed list of classes, so a cow on the road can get called “road”. The goal: flag the pixels of anything unexpected, without knowing what it is.
- **What I did:** In a team of six, trained six models on one shared split, chose thresholds on validation only and judged them once on nine sealed test photographs. My pair built the autoencoders: a pixel baseline and a feature-space one on frozen VGG16 features.
- **Result:** The feature autoencoder is the only model meeting all four business criteria, with the fewest false alarms (10 of 22 flagged blobs); DeepLabV3+ finds the most obstacles (20 of 22). Nine photographs is small, so the top three are not statistically separated — and the write-up says so.
- <sub>Built with TensorFlow · Keras · Autoencoder · VGG16 · FastAPI · Docker</sub>

**7. Unified three source systems into one star-schema warehouse (team of six)**  
<sub>[EventZilla](https://github.com/adriansalvadorekomo/EventZilla-BI-AI-Powered-Event-Analytics-Platform)</sub>

- **What I did:** With a six-person academic team, built a star-schema warehouse over 3 source systems, Prophet demand forecasting and 11 Dockerized microservices behind nginx, orchestrated with Airflow and monitored with Prometheus + Grafana.
- **Result:** Forecast error under 15% (MAPE).
- <sub>Built with Airflow · MLflow · n8n · Docker · Nginx · Prometheus · Grafana</sub>

## Notes

Study notes and project write-ups, with the numbers left honest ([all notes](https://adriansalvadorekomodev.vercel.app/blog)):

- [A test set you open once: how six road-anomaly models were compared](https://adriansalvadorekomodev.vercel.app/blog/test-set-you-open-once)
- [The dataset has no labels. Start with zero-shot, not a classifier.](https://adriansalvadorekomodev.vercel.app/blog/no-labels-zero-shot-first)
- [Your RAG chapter summary skips 95% of the chapter](https://adriansalvadorekomodev.vercel.app/blog/chapter-summaries-skip-95-percent)
- [Put the quality gate between Silver and Gold, and make it fail fast](https://adriansalvadorekomodev.vercel.app/blog/fail-fast-dq-gate-lakehouse)

## Experience

**DevOps Intern, RIF (Rassemblement des Ingénieurs Francophones)**, France, remote, Jul 2026 to Sep 2026. See project 2 above.

## Education

- **ESPRIT School of Engineering**: Engineering, Computer Science, ERP-BI / Data Engineering (5th year), Sep 2022 to Dec 2026
- **Philipps-Universität Marburg**: Exchange student (Freemover), Mathematics and Computer Science, Oct 2026 to present

## Certifications and trainings

- Get Started with Databricks for Data Engineering, Databricks Academy, Sep 2026 (training) · [PDF](certs/databricks-get-started-data-engineering.pdf)
- Data Engineer Associate, DataCamp, 2026 · [certificate](https://www.datacamp.com/certificate/DEA0018198901240)
- SQL Associate, DataCamp, 2026 · [certificate](https://www.datacamp.com/certificate/SQA0019633928960)
- Python Data Associate, DataCamp, 2026 · [certificate](https://www.datacamp.com/certificate/PDA0019443332398)
- Hedera Certified Developer Associate, The Hashgraph Association, Oct 2026 · [PDF](certs/HCDA.pdf)
- Hedera Business Foundation, The Hashgraph Association, Oct 2026 · [PDF](certs/HBF.pdf)

## Languages

Spanish (native) · English (C1) · French (C1) · German (A1, learning)

## Tools

The tools behind the projects above, for reference.

- **Data:** Databricks, Delta Lake, PySpark, Spark SQL, Spark Streaming, Airflow, Prefect, MLflow, star-schema modelling
- **Platform and delivery:** Terraform, Ansible, OpenStack, Docker, Kubernetes, Jenkins, SonarQube, GitHub Actions, Nginx, Linux, Prometheus, Grafana
- **Languages:** Python, SQL, Bash, Java
