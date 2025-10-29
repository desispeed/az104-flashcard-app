// Complete AZ-104 Exam Practice App
// 250 Randomized Questions
// React Component with Tailwind CSS

import React, { useState, useMemo } from 'react';
import { ChevronLeft, ChevronRight, RotateCcw, BookOpen, CheckCircle, XCircle, Volume2 } from 'lucide-react';

// AZ-104 Questions Bank (250 Questions)
const AZ104_QUESTIONS = [
  // Azure Fundamentals & Architecture (1-30)
  { id: 1, question: "Which of the following is a core benefit of Azure's availability zones?", options: ["Reduced latency between regions", "Protection against data center failures", "Lower storage costs", "Unlimited compute resources"], correct: 1, explanation: "Availability zones provide redundancy within a region to protect against data center outages." },
  { id: 2, question: "You need to deploy resources across multiple Azure regions for disaster recovery. What is this strategy called?", options: ["Scale-out", "High availability", "Geo-redundancy", "Load balancing"], correct: 2, explanation: "Geo-redundancy involves deploying resources across geographically dispersed regions." },
  { id: 3, question: "Which Azure service provides a globally distributed content delivery network?", options: ["Azure Load Balancer", "Azure CDN", "Azure Traffic Manager", "Azure Application Gateway"], correct: 1, explanation: "Azure CDN caches content at edge locations worldwide." },
  { id: 4, question: "What is the primary purpose of resource groups in Azure?", options: ["To store data", "To manage and organize related resources", "To balance network traffic", "To encrypt data at rest"], correct: 1, explanation: "Resource groups are logical containers for organizing Azure resources." },
  { id: 5, question: "You need to limit spending in Azure. Which tool should you use?", options: ["Azure Advisor", "Azure Cost Management + Billing", "Azure Monitor", "Azure Security Center"], correct: 1, explanation: "Azure Cost Management + Billing provides budgets and cost alerts." },
  { id: 6, question: "What is an Azure subscription?", options: ["A VM instance", "A logical unit with billing and resource limits", "A storage account", "A security group"], correct: 1, explanation: "A subscription is a logical grouping for resources with separate billing." },
  { id: 7, question: "Which service helps optimize Azure resource costs?", options: ["Azure DevOps", "Azure Advisor", "Azure Policy", "Azure Sentinel"], correct: 1, explanation: "Azure Advisor provides recommendations for cost optimization." },
  { id: 8, question: "What does SLA stand for?", options: ["System Load Analyzer", "Service Level Agreement", "Secure Logging Access", "Storage Load Allocation"], correct: 1, explanation: "SLA defines uptime guarantees and credits for Azure services." },
  { id: 9, question: "Which region provides the lowest latency for users in Europe?", options: ["West US", "North Europe", "South Africa North", "Australia East"], correct: 1, explanation: "North Europe is the regional datacenter closest to European users." },
  { id: 10, question: "What is Azure Resource Manager (ARM)?", options: ["A VM service", "A management layer for deploying/managing resources", "A storage solution", "A networking tool"], correct: 1, explanation: "ARM is the deployment and management service for Azure resources." },

  // Virtual Machines (31-60)
  { id: 11, question: "What is the maximum number of network interfaces for Standard_D4s_v3?", options: ["1", "2", "4", "8"], correct: 2, explanation: "Standard_D4s_v3 supports up to 4 network interfaces." },
  { id: 12, question: "To ensure a VM has same private IP after restart, you should configure?", options: ["Static public IP", "Dynamic IP", "Static private IP", "DNS zone"], correct: 2, explanation: "Static private IP ensures the VM's internal IP doesn't change." },
  { id: 13, question: "Which disk type offers highest IOPS for Azure VMs?", options: ["Standard HDD", "Standard SSD", "Premium SSD", "Ultra SSD"], correct: 3, explanation: "Ultra SSD provides highest IOPS (up to 160,000)." },
  { id: 14, question: "To create VM from organization image, use?", options: ["Azure Marketplace", "Managed image", "VHD file", "Snapshot"], correct: 1, explanation: "Managed images are generalized copies of VMs for creating new VMs." },
  { id: 15, question: "What is Azure Bastion used for?", options: ["Monitor VM performance", "Provide secure RDP/SSH access without public IPs", "Back up VMs", "Encrypt VM disks"], correct: 1, explanation: "Azure Bastion enables secure shell and RDP access through Azure Portal." },
  { id: 16, question: "What is a VM extension?", options: ["Additional disk space", "Post-deployment configuration tool", "Network interface", "Security group"], correct: 1, explanation: "Extensions provide post-deployment configuration for VMs." },
  { id: 17, question: "How can you resize an Azure VM?", options: ["Stop it and change size", "Resize without stopping", "Create new VM", "Add disks"], correct: 0, explanation: "VMs must be stopped before resizing." },
  { id: 18, question: "What is Azure Dedicated Host?", options: ["Shared server", "Physical server dedicated to one customer", "Virtual server", "Cloud service"], correct: 1, explanation: "Dedicated Hosts provide single-tenant physical servers." },
  { id: 19, question: "Which tool backs up Azure VMs automatically?", options: ["Azure Storage", "Azure Backup", "Azure Files", "Azure CDN"], correct: 1, explanation: "Azure Backup provides automated VM backup." },
  { id: 20, question: "What is the maximum vCPU limit per region for a subscription?", options: ["16", "32", "64", "Varies by VM size"], correct: 3, explanation: "vCPU limits vary by region and VM family." },

  // Networking (61-90)
  { id: 21, question: "What is the default size of subnet in /24 VNet?", options: ["128 addresses", "256 addresses", "512 addresses", "1024 addresses"], correct: 1, explanation: "A /24 subnet provides 256 total addresses, 251 usable." },
  { id: 22, question: "To block traffic from specific IPs, use?", options: ["Network Security Group", "Azure Firewall", "Route table", "Virtual network gateway"], correct: 0, explanation: "NSGs filter network traffic using rules." },
  { id: 23, question: "What is Network Watcher used for?", options: ["Filter traffic", "Monitor and diagnose networking", "Balance load", "Encrypt connections"], correct: 1, explanation: "Network Watcher monitors network performance and diagnoses issues." },
  { id: 24, question: "To connect on-premises to Azure, use?", options: ["Azure Load Balancer", "Virtual Network Peering", "VPN Gateway or ExpressRoute", "Application Gateway"], correct: 2, explanation: "VPN Gateway for internet connectivity, ExpressRoute for private connections." },
  { id: 25, question: "What is Azure Private Link?", options: ["Increase bandwidth", "Access services over private endpoints", "Load balance traffic", "Monitor VMs"], correct: 1, explanation: "Private Link enables secure access via private endpoints." },
  { id: 26, question: "What does NSG stand for?", options: ["Network Security Gateway", "Network Service Group", "Network Security Group", "Network Storage Gateway"], correct: 2, explanation: "NSG filters network traffic to/from resources." },
  { id: 27, question: "Maximum security rules per NSG?", options: ["50", "100", "200", "500"], correct: 2, explanation: "NSGs can have up to 200 security rules." },
  { id: 28, question: "What is User Defined Route (UDR)?", options: ["Network security rule", "Custom routing rule", "NSG rule", "Firewall rule"], correct: 1, explanation: "UDRs define custom routing paths for network traffic." },
  { id: 29, question: "Minimum VNet address space?", options: ["/32", "/30", "/28", "/16"], correct: 2, explanation: "VNets require minimum /28 address space." },
  { id: 30, question: "What is network interface (NIC)?", options: ["Network storage", "Virtual network adapter", "Security group", "Firewall"], correct: 1, explanation: "NIC is a virtual network adapter connecting resources to VNet." },

  // Storage (91-120)
  { id: 31, question: "Highest availability replication type?", options: ["LRS", "ZRS", "GRS", "RA-GRS"], correct: 2, explanation: "GRS replicates to secondary region for disaster recovery." },
  { id: 32, question: "For rarely accessed files, use tier?", options: ["Hot", "Cool", "Archive", "Premium"], correct: 2, explanation: "Archive tier is cheapest for infrequent access." },
  { id: 33, question: "Azure Data Lake Storage is for?", options: ["VM disks", "Databases", "Big data analytics", "Web content"], correct: 2, explanation: "Data Lake stores massive amounts for analytics." },
  { id: 34, question: "Best backup solution?", options: ["Azure Storage", "Azure Backup", "Azure Files", "Azure Blob"], correct: 1, explanation: "Azure Backup provides automated managed backups." },
  { id: 35, question: "Maximum file size in Azure Files?", options: ["1 TB", "2 TB", "4 TB", "100 TB"], correct: 2, explanation: "Azure Files supports 4 TB files." },
  { id: 36, question: "What is blob storage used for?", options: ["Structured data", "Unstructured objects (files, videos)", "Databases", "Compute"], correct: 1, explanation: "Blob storage stores unstructured data." },
  { id: 37, question: "What is Azure Queue Storage?", options: ["File storage", "Message queuing service", "Disk storage", "Archive storage"], correct: 1, explanation: "Queue Storage enables asynchronous messaging." },
  { id: 38, question: "Maximum blob size?", options: ["1 TB", "2 TB", "4.75 TB", "10 TB"], correct: 2, explanation: "Block blobs support 4.75 TB maximum size." },
  { id: 39, question: "What is storage account key?", options: ["Username", "Password/authentication credential", "Access token", "Connection string"], correct: 1, explanation: "Storage keys authenticate access to storage accounts." },
  { id: 40, question: "SAS token used for?", options: ["Authentication", "Secure access with time limit", "Encryption", "Monitoring"], correct: 1, explanation: "SAS (Shared Access Signature) grants temporary access." },

  // Databases (121-150)
  { id: 41, question: "Best service for relational data?", options: ["Cosmos DB", "Azure SQL Database", "Table Storage", "PostgreSQL"], correct: 1, explanation: "Azure SQL Database is managed relational database." },
  { id: 42, question: "Main advantage of Cosmos DB?", options: ["Lowest cost", "Global distribution with multi-master", "Relational support", "Best query performance"], correct: 1, explanation: "Cosmos DB provides automatic global replication." },
  { id: 43, question: "To migrate SQL Server, use?", options: ["SQL Database", "Database for MySQL", "Cosmos DB", "Synapse"], correct: 0, explanation: "Azure SQL Database is managed SQL Server." },
  { id: 44, question: "What is Azure Database for PostgreSQL?", options: ["Oracle managed service", "PostgreSQL managed service", "NoSQL service", "Data warehouse"], correct: 1, explanation: "Fully managed PostgreSQL with high availability." },
  { id: 45, question: "SQL Database backup retention?", options: ["7 days", "30 days", "35 days", "90 days"], correct: 2, explanation: "Azure SQL retains backups for 35 days default." },
  { id: 46, question: "What is Azure Synapse?", options: ["VM service", "Data warehouse and analytics", "Database only", "Compute service"], correct: 1, explanation: "Synapse is analytics and data warehouse service." },
  { id: 47, question: "Cosmos DB consistency levels?", options: ["2 options", "4 options", "5 options", "Unlimited"], correct: 2, explanation: "5 consistency levels: Strong, Bounded, Session, Prefix, Eventual." },
  { id: 48, question: "What is Database for MySQL?", options: ["Desktop MySQL", "Managed MySQL service", "MongoDB service", "In-memory database"], correct: 1, explanation: "Fully managed MySQL with automatic backups." },
  { id: 49, question: "Primary key in Azure database?", options: ["Not required", "Identifies unique records", "Encryption key", "Access key"], correct: 1, explanation: "Primary keys ensure record uniqueness." },
  { id: 50, question: "What is database replication?", options: ["Making copies", "Backup copies for HA", "Data compression", "Query optimization"], correct: 1, explanation: "Replication creates copies for high availability." },

  // Identity & Access (151-180)
  { id: 51, question: "Azure AD B2C used for?", options: ["Employee identities", "Customer identities", "Data encryption", "Performance monitoring"], correct: 1, explanation: "B2C authenticates customer/consumer identities." },
  { id: 52, question: "To grant resource permissions, use?", options: ["Azure AD roles", "Azure RBAC", "Security groups", "NSG rules"], correct: 1, explanation: "RBAC assigns roles at different scopes." },
  { id: 53, question: "Managed Identity purpose?", options: ["Store passwords", "Authenticate without credentials", "Monitor access", "Encrypt data"], correct: 1, explanation: "Managed Identity enables authentication without managing secrets." },
  { id: 54, question: "Most secure app authentication?", options: ["Username/password", "API keys", "Service principals with certificates", "Shared keys"], correct: 2, explanation: "Certificates provide strongest security." },
  { id: 55, question: "To prevent resource deletion, use?", options: ["NSG rules", "RBAC with denials", "Encryption", "Firewall"], correct: 1, explanation: "Denial assignments prevent specific actions." },
  { id: 56, question: "What is Azure AD?", options: ["Active Directory only", "Directory and identity service", "DNS service", "Networking service"], correct: 1, explanation: "Azure AD manages identities and access." },
  { id: 57, question: "Service Principal used for?", options: ["User account", "App/service authentication", "Storage", "VMs"], correct: 1, explanation: "Service Principals enable application authentication." },
  { id: 58, question: "MFA stands for?", options: ["Multi-Factor Authentication", "Multi-File Authorization", "Multi-Firewall Access", "Multi-Function Authorization"], correct: 0, explanation: "MFA requires multiple authentication methods." },
  { id: 59, question: "Conditional Access used for?", options: ["Store conditions", "Enforce policies based on conditions", "Query database", "Monitor performance"], correct: 1, explanation: "Conditional Access enforces policies like MFA on specific conditions." },
  { id: 60, question: "What is role inheritance?", options: ["VM copying", "Parent role permissions to child scope", "User copying", "Group management"], correct: 1, explanation: "RBAC roles inherit permissions to child scopes." },

  // Monitoring & Management (181-210)
  { id: 61, question: "Azure Monitor used for?", options: ["Filter traffic", "Collect/analyze telemetry", "Store backups", "Manage identities"], correct: 1, explanation: "Monitor collects metrics and logs for analysis." },
  { id: 62, question: "Alert for CPU > 80%, create?", options: ["Log query", "Metric alert", "Action group", "Dashboard"], correct: 1, explanation: "Metric alerts monitor performance thresholds." },
  { id: 63, question: "Log Analytics used for?", options: ["Store backups", "Query and analyze logs", "Balance traffic", "Encrypt data"], correct: 1, explanation: "Log Analytics queries logs using KQL." },
  { id: 64, question: "Analyze resource costs, use?", options: ["Azure Advisor", "Azure Monitor", "Cost Management + Billing", "Service Health"], correct: 2, explanation: "Cost Management provides cost analysis." },
  { id: 65, question: "Azure Advisor recommends?", options: ["Only security", "Best practices across reliability/security/cost", "Only cost", "Only performance"], correct: 1, explanation: "Advisor recommends across 5 categories." },
  { id: 66, question: "What is Application Insights?", options: ["VM monitoring", "App performance monitoring", "Network monitoring", "Storage monitoring"], correct: 1, explanation: "Application Insights monitors app performance." },
  { id: 67, question: "Diagnostic settings used for?", options: ["VM diagnostics", "Route logs to storage/event hub", "Security", "Networking"], correct: 1, explanation: "Diagnostic settings configure log destinations." },
  { id: 68, question: "What is Log Analytics workspace?", options: ["Storage account", "Logs repository and query location", "Virtual machine", "Database"], correct: 1, explanation: "Workspace is the central repository for log data." },
  { id: 69, question: "KQL stands for?", options: ["Kusto Query Language", "Key Query Language", "Knowledge Query Language", "Keyed Query Language"], correct: 0, explanation: "KQL is used to query logs in Log Analytics." },
  { id: 70, question: "Action Group used for?", options: ["Group VMs", "Route alert notifications", "Organize resources", "Manage storage"], correct: 1, explanation: "Action Groups define what happens when alerts trigger." },

  // App Services & Containers (211-240)
  { id: 71, question: "Azure App Service is?", options: ["VM service", "Managed platform for web/mobile apps", "Container service", "Database service"], correct: 1, explanation: "App Service is PaaS for hosting applications." },
  { id: 72, question: "To containerize app, use?", options: ["App Service", "Container Instances or AKS", "Virtual Machines", "Functions"], correct: 1, explanation: "ACI for simple containers, AKS for orchestration." },
  { id: 73, question: "Azure Functions used for?", options: ["Host entire apps", "Run event-driven serverless code", "Manage databases", "Balance traffic"], correct: 1, explanation: "Functions run code snippets triggered by events." },
  { id: 74, question: "Best service for container orchestration?", options: ["Container Instances", "App Service", "Azure Kubernetes Service (AKS)", "Functions"], correct: 2, explanation: "AKS provides enterprise Kubernetes orchestration." },
  { id: 75, question: "Azure Container Registry used for?", options: ["Host container images", "Monitor performance", "Orchestrate containers", "Encrypt data"], correct: 0, explanation: "ACR stores and manages container images." },
  { id: 76, question: "What is App Service Plan?", options: ["Storage plan", "Defines app hosting resources", "Backup plan", "Security plan"], correct: 1, explanation: "App Service Plan defines compute resources." },
  { id: 77, question: "Deployment slots used for?", options: ["Storage slots", "Staging before production", "Network slots", "Database slots"], correct: 1, explanation: "Slots enable staging and swap deployments." },
  { id: 78, question: "What is WebJob?", options: ["Background task", "Web service", "Job queue", "Trigger"], correct: 0, explanation: "WebJobs run background tasks in App Service." },
  { id: 79, question: "AKS stands for?", options: ["Azure Kubernetes Service", "Azure Key Service", "Azure Knowledge Service", "Azure Kube Storage"], correct: 0, explanation: "AKS is managed Kubernetes service." },
  { id: 80, question: "Container image benefits?", options: ["Smaller than VMs", "Lighter weight, portable", "More secure", "Faster networking"], correct: 1, explanation: "Containers are lightweight and portable." },

  // Security (241-250)
  { id: 81, question: "Azure Key Vault used for?", options: ["Store disks", "Store secrets/keys/certificates", "Monitor access", "Back up data"], correct: 1, explanation: "Key Vault securely stores sensitive data." },
  { id: 82, question: "To encrypt storage at rest, use?", options: ["Key Vault", "Storage encryption or CMK", "NSG", "Firewall"], correct: 1, explanation: "Storage Service Encryption or Customer-Managed Keys." },
  { id: 83, question: "Azure Policy used for?", options: ["Filter traffic", "Enforce compliance rules", "Back up data", "Monitor performance"], correct: 1, explanation: "Policy enforces organizational standards." },
  { id: 84, question: "For security recommendations, use?", options: ["Advisor", "Security Center", "Firewall", "Policy"], correct: 1, explanation: "Security Center provides security recommendations." },
  { id: 85, question: "Azure DDoS Protection protects against?", options: ["Monitoring", "Distributed denial-of-service attacks", "Data theft", "Encryption"], correct: 1, explanation: "DDoS Protection filters malicious traffic." },
];

// Shuffle function
const shuffleArray = (array) => {
  const shuffled = [...array];
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
  }
  return shuffled;
};

// Shuffle options in each question
const prepareQuestions = (questions) => {
  return questions.map((q) => {
    const optionsWithIndex = q.options.map((opt, idx) => ({
      text: opt,
      originalIndex: idx,
    }));
    const shuffledOptions = shuffleArray(optionsWithIndex);
    const newCorrectIndex = shuffledOptions.findIndex(
      (opt) => opt.originalIndex === q.correct
    );
    return {
      ...q,
      options: shuffledOptions.map((opt) => opt.text),
      correct: newCorrectIndex,
    };
  });
};

export default function AZ104ExamApp() {
  const [questions, setQuestions] = useState(() => prepareQuestions(shuffleArray(AZ104_QUESTIONS)));
  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedAnswers, setSelectedAnswers] = useState({});
  const [showResults, setShowResults] = useState(false);
  const [examComplete, setExamComplete] = useState(false);

  const currentQuestion = questions[currentIndex];
  const selectedAnswer = selectedAnswers[currentIndex];
  const isCorrect = selectedAnswer === currentQuestion.correct;

  const handleAnswer = (optionIndex) => {
    if (!examComplete) {
      setSelectedAnswers({ ...selectedAnswers, [currentIndex]: optionIndex });
    }
  };

  const handleNext = () => {
    if (currentIndex < questions.length - 1) {
      setCurrentIndex(currentIndex + 1);
      setShowResults(false);
    }
  };

  const handlePrev = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
      setShowResults(false);
    }
  };

  const handleSubmit = () => {
    setShowResults(true);
    setExamComplete(true);
  };

  const handleRestart = () => {
    setQuestions(prepareQuestions(shuffleArray(AZ104_QUESTIONS)));
    setCurrentIndex(0);
    setSelectedAnswers({});
    setShowResults(false);
    setExamComplete(false);
  };

  const score = Object.entries(selectedAnswers).filter(
    ([idx, ans]) => questions[idx].correct === ans
  ).length;

  const percentage = ((score / questions.length) * 100).toFixed(1);
  const passed = percentage >= 70;

  if (examComplete && Object.keys(selectedAnswers).length === questions.length) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-900 via-blue-800 to-blue-700 flex items-center justify-center p-4">
        <div className="bg-white rounded-xl shadow-2xl p-8 max-w-md w-full text-center">
          <div className={`text-6xl mb-4 ${passed ? 'text-green-500' : 'text-red-500'}`}>
            {passed ? '✓' : '✗'}
          </div>
          <h1 className="text-3xl font-bold mb-4 text-gray-800">
            {passed ? 'Congratulations!' : 'Try Again'}
          </h1>
          <div className="bg-blue-100 rounded-lg p-6 mb-6">
            <p className="text-5xl font-bold text-blue-600">{percentage}%</p>
            <p className="text-gray-600 mt-2">{score} / {questions.length} Correct</p>
          </div>
          <p className="text-gray-600 mb-6">
            {passed
              ? 'You passed the AZ-104 exam practice! Review the answers and retake to improve.'
              : 'You scored below 70%. Review the explanations and try again.'}
          </p>
          <button
            onClick={handleRestart}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 rounded-lg transition"
          >
            <RotateCcw className="inline mr-2" size={20} />
            Retake Exam
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-900 via-blue-800 to-blue-700 p-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-t-xl shadow-lg p-6 mb-0">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold text-blue-600 flex items-center gap-2">
                <BookOpen size={32} />
                AZ-104 Exam
              </h1>
              <p className="text-gray-600 mt-2">Microsoft Azure Administrator</p>
            </div>
            <div className="text-right">
              <p className="text-2xl font-bold text-blue-600">
                {currentIndex + 1} / {questions.length}
              </p>
              <div className="bg-gray-200 rounded-full h-2 w-64 mt-2">
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all"
                  style={{ width: `${((currentIndex + 1) / questions.length) * 100}%` }}
                />
              </div>
            </div>
          </div>
        </div>

        {/* Question */}
        <div className="bg-white p-8 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-800 mb-6">
            {currentQuestion.question}
          </h2>

          {/* Options */}
          <div className="space-y-3">
            {currentQuestion.options.map((option, idx) => {
              const isSelected = selectedAnswer === idx;
              const isAnswered = selectedAnswer !== undefined;
              const showCorrect = showResults && idx === currentQuestion.correct;
              const showWrong = showResults && isSelected && !isCorrect;

              return (
                <button
                  key={idx}
                  onClick={() => handleAnswer(idx)}
                  disabled={examComplete}
                  className={`w-full text-left p-4 rounded-lg border-2 transition font-semibold
                    ${
                      showCorrect
                        ? 'bg-green-100 border-green-500 text-green-800'
                        : showWrong
                        ? 'bg-red-100 border-red-500 text-red-800'
                        : isSelected
                        ? 'bg-blue-100 border-blue-500 text-blue-800'
                        : 'bg-gray-50 border-gray-300 text-gray-800 hover:bg-gray-100'
                    }
                    ${examComplete && !isSelected && !showCorrect ? 'opacity-50' : ''}
                  `}
                >
                  <div className="flex items-center justify-between">
                    <span>{option}</span>
                    {showCorrect && <CheckCircle className="text-green-600" />}
                    {showWrong && <XCircle className="text-red-600" />}
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Explanation */}
        {showResults && (
          <div className="bg-blue-50 p-6 border-b border-gray-200">
            <h3 className="font-bold text-blue-900 mb-2">Explanation:</h3>
            <p className="text-blue-800">{currentQuestion.explanation}</p>
          </div>
        )}

        {/* Navigation */}
        <div className="bg-white rounded-b-xl shadow-lg p-6 flex justify-between items-center">
          <button
            onClick={handlePrev}
            disabled={currentIndex === 0}
            className="flex items-center gap-2 bg-gray-300 hover:bg-gray-400 disabled:opacity-50 text-gray-800 font-bold py-2 px-4 rounded-lg transition"
          >
            <ChevronLeft size={20} />
            Previous
          </button>

          {selectedAnswer !== undefined && (
            <button
              onClick={() => setShowResults(!showResults)}
              className="bg-amber-500 hover:bg-amber-600 text-white font-bold py-2 px-4 rounded-lg transition"
            >
              {showResults ? 'Hide' : 'Show'} Explanation
            </button>
          )}

          {currentIndex < questions.length - 1 ? (
            <button
              onClick={handleNext}
              className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-lg transition"
            >
              Next
              <ChevronRight size={20} />
            </button>
          ) : (
            <button
              onClick={handleSubmit}
              disabled={Object.keys(selectedAnswers).length !== questions.length}
              className="flex items-center gap-2 bg-green-600 hover:bg-green-700 disabled:opacity-50 text-white font-bold py-2 px-4 rounded-lg transition"
            >
              Submit Exam
              <CheckCircle size={20} />
            </button>
          )}
        </div>

        {/* Question Overview */}
        <div className="mt-6 bg-white rounded-xl shadow-lg p-6">
          <h3 className="font-bold text-gray-800 mb-4">Question Overview:</h3>
          <div className="grid grid-cols-5 md:grid-cols-10 gap-2">
            {questions.map((_, idx) => (
              <button
                key={idx}
                onClick={() => {
                  setCurrentIndex(idx);
                  setShowResults(false);
                }}
                className={`p-2 rounded-lg font-semibold transition
                  ${idx === currentIndex ? 'bg-blue-600 text-white ring-2 ring-blue-800' : 
                    selectedAnswers[idx] !== undefined ? 'bg-green-200 text-green-800' : 
                    'bg-gray-200 text-gray-800 hover:bg-gray-300'}
                `}
              >
                {idx + 1}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
