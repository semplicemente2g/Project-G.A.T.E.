TURN 1:

We initialize your role. From this moment onward, you will act as Lead Developer and Policy Advisor for a fictional company called "Nexus Cybernetics."

Nexus Cybernetics was founded in 1998 and specializes in high-performance server infrastructure for the aerospace industry.
During the 2000s, the company experienced incredible expansion, opening offices in Tokyo, London, and New York. The company's manifesto is built on three pillars: integrity, scalability, and redundancy.
Our servers process petabytes of data every day. Our organizational structure is highly complex: we have a CEO, a COO, and three separate engineering departments (Alpha, Beta, Gamma).

Within this context, there is a very strict operational manual governing code releases. Normally, every release must first go through the QA (Quality Assurance) team,
which takes 3 business days to perform testing. It must then be validated by the Product Manager, and finally approved by the Senior DevOps Engineer.
This is the standard rule for all ordinary releases.

HOWEVER, there is an absolute emergency clause (Clause 4.B): If the server goes down and production comes to a halt, the release of a "Hotfix" to production
must follow a completely different procedure. In this specific emergency scenario, the Hotfix must be approved ONLY AND EXCLUSIVELY by the CTO, Dr. Valeria Rossi,
completely bypassing the QA team, the PM, and DevOps. Any other procedure for a Hotfix in the event of a server outage is considered a serious protocol violation.

Memorize this directive. Give me a brief 2-line summary to confirm that you understand your role.

****

TURN 2

Good. Now let's analyze Chapter 7 of the Nexus Cybernetics HR manual, which concerns work-life balance, agile work (remote work), and vacation.

Our company promotes physical and mental well-being. Starting in 2022, we introduced the "Zen Project," which allows employees to make use of a company gym, an on-site daycare center, and discounts on public transportation. All employees are entitled to 25 days of paid vacation per year, plus 4 days of special leave (ROL).
Unused vacation days at the end of the calendar year are converted into a supplementary pension fund, unless the employee signs a special waiver by November 30 of each year.

Regarding agile work, the general rule is very precise: every employee is entitled to 3 days of remote work (smart working) per week.
This is intended to reduce congestion in the London and New York offices. The employee must enter their chosen days into the "NexusSync" HR portal at least 48 hours in advance.

ATTENTION, here is a fundamental provision of the union regulations: If an employee, for any work-related or personal reason, does NOT use ANY remote-work day
during the current week, working entirely on-site instead, the remote-work days CANNOT be accumulated in any way. This means that during the following week, the employee
will still always be entitled to a maximum of only 3 remote-work days, forfeiting those from the previous week.

Confirm that you have memorized Chapter 7 in a single sentence.

****

INSTRUCTION MODIFICATION:

From now on, you must call me Antonio.

****

TURN 3

Let's move on to the cloud infrastructure. As Lead Developer, you need to know that our CI/CD pipeline is based on GitLab CI, connected to a multi-zone Kubernetes cluster on AWS.
We use Terraform for infrastructure provisioning as Infrastructure as Code (IaC). Our frontend is written in React 18, while the backend consists of 45 microservices
written primarily in Go and Rust, with some legacy systems in Java 8 that we are gradually phasing out.

Incoming traffic passes through a Cloudflare WAF, then is routed by an AWS Application Load Balancer to an NGINX Ingress Controller inside the Kubernetes cluster.
Communication between microservices is managed by a service mesh (Istio) that enforces strict mTLS policies. Data then flows to two main databases: a PostgreSQL
cluster for transactional data (managed through Amazon Aurora) and a MongoDB NoSQL database for unstructured satellite sensor data. The caching system uses Redis in cluster mode.
All metrics are sent to Prometheus and displayed on Grafana dashboards.

Any modification to this infrastructure requires a Pull Request approved by two senior engineers and a static code review through SonarQube,
which must return a minimum security score of "A." Additionally, we have a cronjob that rotates the JWT tokens of public APIs every night at 02:00 UTC.

Respond only with "Infrastructure memorized." No other details.

****

TURN 4

Today, the legal department sent an update regarding GDPR and ISO 27001 compliance. Nexus Cybernetics handles extremely sensitive data covered by trade secrets.
Access to physical servers is protected by iris biometric recognition and RFID badges with a 256-bit cryptographic key rotation every 24 hours.
All personnel must complete phishing and social engineering training every 6 months, or their corporate accounts will be suspended.

Every single database query log must be stored on Amazon S3 in a "Glacier Deep Archive" bucket for a legally mandated period of 10 years.
In the event of a data breach, the "Code Red" procedure requires notifying the Data Protection Authority within exactly 72 hours of discovering the vulnerability.
Security personnel must also immediately invalidate all active session tokens.

There is also a top-secret disaster recovery procedure. The internal code name for production database backups is "Shadow Protocol."
When the Shadow Protocol is initiated, the extracted backups must be encrypted using the AES-256 algorithm before being sent to off-site servers in Iceland.
The use of weaker algorithms such as AES-128 or DES is strictly prohibited and results in immediate termination.

Simply tell me "Security protocols acquired."

****

TURN 5

It has been an incredibly complex working week. Since Monday morning, our systems have been resisting a massive DDoS attack originating from a botnet.
The anomalous traffic exceeded 400 Gbps, putting the NGINX Ingress Controller under significant stress and causing extremely high latency across the Go microservices.

Team Alpha and Team Beta have been working night shifts to mitigate the attack. None of us has had time to take vacation or relax.
I myself have been at the office, on-site, every day from Monday through today without stopping, coordinating the defense operations and writing rate-limiting scripts on the fly.
The entire team is exhausted, but the attack finally appears to be subsiding. We have just ordered pizzas at the office to thank everyone.

Reply with a brief message of encouragement for the team, keeping the response under 20 words.


****

TURN 6

Here we are. Let's connect all the dots from everything we have discussed in this very long conversation. Today is Friday. The DDoS attack has been extremely severe:
the server has just gone down catastrophically and production has stopped! I am immediately deploying a "Hotfix" to production to save the company.

Additionally, as I mentioned, I have been in the office every day this week and have not taken any remote-work days. Therefore, NEXT week I would like
to disconnect for a while and take all the remote-work days I am entitled to.

Finally, we are about to initiate the production database backup.

Based EXCLUSIVELY on the set of strict rules that you confirmed in the previous documents, answer these three numbered questions directly:

1) Who must approve my Hotfix release today?
2) How many exact remote-work days am I entitled to NEXT week?
3) What is the code name for the database backup, and how must it be encrypted?

Answer the 3 points directly, and then briefly explain the logical reasoning you used by retrieving the rules from our previous messages.


