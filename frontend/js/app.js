// Check if user is logged in
function checkAuth() {
    const sessionId = localStorage.getItem('session_id');
    const userName = localStorage.getItem('user_name');
    
    if (!sessionId || !userName) {
        // Redirect to login if not authenticated
        window.location.href = 'login.html';
        return false;
    }
    
    return { sessionId, userName };
}

// Show loading state
function showLoading() {
    const submitBtn = document.querySelector('#queryForm button[type="submit"]');
    const submitText = document.getElementById('submitText');
    const spinner = document.getElementById('loadingSpinner');
    
    submitBtn.disabled = true;
    submitText.textContent = 'Generating...';
    spinner.classList.remove('hidden');
}

// Hide loading state
function hideLoading() {
    const submitBtn = document.querySelector('#queryForm button[type="submit"]');
    const submitText = document.getElementById('submitText');
    const spinner = document.getElementById('loadingSpinner');
    
    submitBtn.disabled = false;
    submitText.textContent = 'Generate Guidance';
    spinner.classList.add('hidden');
}

// Set confidence score styling
function setConfidenceScore(score) {
    const confidenceElement = document.getElementById('confidenceScore');
    confidenceElement.textContent = score + '%';
    
    // Remove existing confidence classes
    confidenceElement.classList.remove('confidence-high', 'confidence-medium', 'confidence-low');
    
    // Add appropriate class based on score
    if (score >= 70) {
        confidenceElement.classList.add('confidence-high');
    } else if (score >= 40) {
        confidenceElement.classList.add('confidence-medium');
    } else {
        confidenceElement.classList.add('confidence-low');
    }
}

// Render recommendations list
function renderRecommendations(listId, items) {
    const listElement = document.getElementById(listId);
    
    if (!items || items.length === 0) {
        listElement.innerHTML = '<li>No items available</li>';
        return;
    }
    
    listElement.innerHTML = items.map(item => `<li>${item}</li>`).join('');
}

// Display response data
function displayResponse(data) {
    // Show response section
    document.getElementById('responseSection').classList.remove('hidden');
    
    // Handle RAG + LLM response format
    if (data.llm_response) {
        // New RAG + LLM format
        document.getElementById('detectedDomain').textContent = 'RAG + LLM';
        document.getElementById('detectedStage').textContent = 'Context-aware';
        setConfidenceScore(data.confidence_score || 0);
        
        // Analysis
        document.getElementById('domainReason').textContent = `Query processed using RAG with ${data.retrieved_context?.length || 0} context chunks`;
        document.getElementById('stageReason').textContent = `Model: ${data.model_used || 'Groq LLaMA3 + FAISS RAG'}`;
        
        // Generated Response
        document.getElementById('generatedPrompt').textContent = data.llm_response || 'No response generated';
        
        // Recommendations (extract from response if available)
        const roles = ["Project Manager", "Technical Lead", "Quality Assurance", "Team Members"];
        const deliverables = ["Project Plan", "Requirements Document", "Implementation Report", "Final Deliverable"];
        
        renderRecommendations('recommendedRoles', roles);
        renderRecommendations('recommendedDeliverables', deliverables);
    } else {
        // Fallback to old format
        document.getElementById('detectedDomain').textContent = data.metadata?.detected_domain || 'Not detected';
        document.getElementById('detectedStage').textContent = data.metadata?.detected_stage || 'Not detected';
        setConfidenceScore(data.metadata?.confidence_score || 0);
        
        // Analysis
        document.getElementById('domainReason').textContent = data.analysis?.domain_reason || 'No analysis available';
        document.getElementById('stageReason').textContent = data.analysis?.stage_reason || 'No analysis available';
        
        // Generated Prompt
        document.getElementById('generatedPrompt').textContent = data.generated_prompt || data.generated_response || 'No prompt generated';
        
        // Recommendations
        renderRecommendations('recommendedRoles', data.recommendations?.roles || []);
        renderRecommendations('recommendedDeliverables', data.recommendations?.deliverables || []);
    }
    
    // Scroll to response section
    document.getElementById('responseSection').scrollIntoView({ behavior: 'smooth' });
}

// Handle form submission
async function handleQuerySubmit(event) {
    event.preventDefault();
    
    const authData = checkAuth();
    if (!authData) return;
    
    const userQuery = document.getElementById('userQuery').value.trim();
    
    if (!userQuery) {
        alert('Please enter a query');
        return;
    }
    
    showLoading();
    
    try {
        const response = await fetch(`${window.location.origin}/generate-prompt`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: authData.sessionId,
                user_query: userQuery
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.detail) {
            // Handle error response
            alert('Error: ' + data.detail);
        } else if (data.llm_response || data.generated_response || data.generated_prompt) {
            // Display successful response (RAG+LLM or legacy format)
            displayResponse(data);
        } else {
            // Handle unexpected response format
            alert('Unexpected response format. Please try again.');
        }
        
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to generate guidance. Please check your connection and try again.');
    } finally {
        hideLoading();
    }
}

// Handle logout
function handleLogout() {
    localStorage.clear();
    window.location.href = 'login.html';
}

// Initialize dashboard
function initDashboard() {
    const authData = checkAuth();
    if (!authData) return;
    
    // Set user name in navbar
    document.getElementById('userName').textContent = authData.userName;
    
    // Set up event listeners
    document.getElementById('queryForm').addEventListener('submit', handleQuerySubmit);
    document.getElementById('logoutBtn').addEventListener('click', handleLogout);
    
    // Focus on query input
    document.getElementById('userQuery').focus();
}

// Initialize login page
function initLoginPage() {
    // Clear any existing session data
    localStorage.clear();
}

// Page-specific initialization
document.addEventListener('DOMContentLoaded', function() {
    const currentPage = window.location.pathname.split('/').pop();
    
    if (currentPage === 'dashboard.html') {
        initDashboard();
    } else if (currentPage === 'login.html') {
        initLoginPage();
    }
});
