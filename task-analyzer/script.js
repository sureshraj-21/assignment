// ============================================
// Task Analyzer Frontend - Main Application
// ============================================

class TaskAnalyzer {
    constructor() {
        this.tasks = [];
        this.results = null;
        this.currentStrategy = 'smart';
        this.apiUrl = 'http://127.0.0.1:8000/api/tasks';
        this.feedbackStats = {}; // Track helpful/unhelpful ratings per task
        
        this.initializeElements();
        this.attachEventListeners();
        this.loadFromLocalStorage();
        this.loadFeedbackStats();
    }

    // ============================================
    // Initialization
    // ============================================

    initializeElements() {
        // Input elements
        this.taskForm = document.getElementById('taskForm');
        this.taskTitle = document.getElementById('taskTitle');
        this.taskPriority = document.getElementById('taskPriority');
        this.taskEffort = document.getElementById('taskEffort');
        this.taskDueDate = document.getElementById('taskDueDate');
        this.taskDependencies = document.getElementById('taskDependencies');
        this.jsonImport = document.getElementById('jsonImport');
        this.strategyDropdown = document.getElementById('strategy');
        
        // Preview elements
        this.tasksPreview = document.getElementById('tasksPreview');
        
        // Action buttons
        this.analyzeBtn = document.getElementById('analyzeBtn');
        this.clearBtn = document.getElementById('clearBtn');
        this.importBtn = document.getElementById('importBtn');
        
        // Output elements
        this.loadingState = document.getElementById('loadingState');
        this.errorState = document.getElementById('errorState');
        this.errorMessage = document.getElementById('errorMessage');
        this.resultsContainer = document.getElementById('resultsContainer');
        this.emptyState = document.getElementById('emptyState');
        this.resultsList = document.getElementById('resultsList');
        this.cycleAlert = document.getElementById('cycleAlert');
        this.cyclesSection = document.getElementById('cyclesSection');
        this.cyclesList = document.getElementById('cyclesList');
        this.graphSection = document.getElementById('graphSection');
        this.depGraph = document.getElementById('depGraph');
        this.eisenhowerSection = document.getElementById('eisenhowerSection');
        this.q1 = document.getElementById('q1');
        this.q2 = document.getElementById('q2');
        this.q3 = document.getElementById('q3');
        this.q4 = document.getElementById('q4');
        
        // Stats elements
        this.totalTasks = document.getElementById('totalTasks');
        this.highPriorityCount = document.getElementById('highPriorityCount');
        this.cyclesCount = document.getElementById('cyclesCount');
        this.strategyInfo = document.getElementById('strategyInfo');
        
        // Tab elements
        this.tabButtons = document.querySelectorAll('.tab-button');
        this.tabContents = document.querySelectorAll('.tab-content');
    }

    attachEventListeners() {
        // Form submission
        this.taskForm.addEventListener('submit', (e) => this.addTask(e));
        
        // Tab switching
        this.tabButtons.forEach(button => {
            button.addEventListener('click', (e) => this.switchTab(e));
        });
        
        // Import button
        this.importBtn.addEventListener('click', () => this.importJSON());
        
        // Action buttons
        this.analyzeBtn.addEventListener('click', () => this.analyzeTasks());
        this.clearBtn.addEventListener('click', () => this.clearAllTasks());
        
        // Strategy change
        this.strategyDropdown.addEventListener('change', (e) => {
            this.currentStrategy = e.target.value;
        });
    }

    // ============================================
    // Tab Management
    // ============================================

    switchTab(e) {
        const tabName = e.target.dataset.tab;
        
        // Remove active class from all buttons and contents
        this.tabButtons.forEach(btn => btn.classList.remove('active'));
        this.tabContents.forEach(content => content.classList.remove('active'));
        
        // Add active class to clicked button and corresponding content
        e.target.classList.add('active');
        document.getElementById(tabName).classList.add('active');
    }

    // ============================================
    // Task Management
    // ============================================

    addTask(e) {
        e.preventDefault();

        // Validate form
        if (!this.taskTitle.value.trim()) {
            this.showError('Please enter a task title');
            return;
        }

        const task = {
            id: `task_${Date.now()}`,
            title: this.taskTitle.value.trim(),
            priority: parseInt(this.taskPriority.value),
            effort: parseInt(this.taskEffort.value),
            due_date: this.taskDueDate.value || null,
            dependencies: this.parseDependencies(this.taskDependencies.value)
        };

        this.tasks.push(task);
        this.saveToLocalStorage();
        this.updateTasksPreview();
        this.taskForm.reset();
        this.taskPriority.value = 5;
        this.taskEffort.value = 5;

        this.showSuccess('Task added successfully!');
    }

    parseDependencies(input) {
        if (!input.trim()) return [];
        return input.split(',').map(dep => dep.trim()).filter(dep => dep);
    }

    importJSON() {
        try {
            const jsonText = this.jsonImport.value.trim();
            if (!jsonText) {
                this.showError('Please paste JSON data');
                return;
            }

            const importedTasks = JSON.parse(jsonText);
            
            if (!Array.isArray(importedTasks)) {
                this.showError('JSON must be an array of tasks');
                return;
            }

            importedTasks.forEach((task, index) => {
                if (!task.title) {
                    throw new Error(`Task ${index} is missing a title`);
                }

                this.tasks.push({
                    id: task.id || `task_${Date.now()}_${index}`,
                    title: task.title,
                    priority: task.priority || 5,
                    effort: task.effort || 5,
                    due_date: task.due_date || null,
                    dependencies: task.dependencies || []
                });
            });

            this.saveToLocalStorage();
            this.updateTasksPreview();
            this.jsonImport.value = '';

            this.showSuccess(`Successfully imported ${importedTasks.length} tasks!`);
        } catch (error) {
            this.showError(`Invalid JSON: ${error.message}`);
        }
    }

    updateTasksPreview() {
        if (this.tasks.length === 0) {
            this.tasksPreview.innerHTML = '<p class="empty-state">No tasks added yet</p>';
            return;
        }

        this.tasksPreview.innerHTML = this.tasks.map((task, index) => `
            <div class="task-preview-item">
                <strong>${task.title}</strong>
                <button type="button" class="task-preview-remove" onclick="app.removeTask(${index})">Remove</button>
            </div>
        `).join('');
    }

    removeTask(index) {
        this.tasks.splice(index, 1);
        this.saveToLocalStorage();
        this.updateTasksPreview();
    }

    clearAllTasks() {
        if (confirm('Are you sure you want to clear all tasks?')) {
            this.tasks = [];
            this.results = null;
            this.saveToLocalStorage();
            this.updateTasksPreview();
            this.hideResults();
            this.showSuccess('All tasks cleared');
        }
    }

    // ============================================
    // API Communication
    // ============================================

    async analyzeTasks() {
        if (this.tasks.length === 0) {
            this.showError('Please add at least one task before analyzing');
            return;
        }

        this.showLoading();

        try {
            const response = await fetch(`${this.apiUrl}/analyze/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    tasks: this.tasks,
                    strategy: this.currentStrategy
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            this.results = data;
            this.displayResults(data);
            this.hideLoading();
            this.showResults();

        } catch (error) {
            console.error('Error analyzing tasks:', error);
            this.showError(`Failed to analyze tasks: ${error.message}`);
            this.hideLoading();
        }
    }

    // ============================================
    // Results Display
    // ============================================

    displayResults(data) {
        const { tasks, cycle_detected, cycles } = data;

        // Update strategy info
        this.updateStrategyInfo();

        // Update stats
        this.totalTasks.textContent = tasks.length;
        this.highPriorityCount.textContent = tasks.filter(t => t.components.importance_norm >= 0.7).length;
        this.cyclesCount.textContent = cycles.length;

        // Show cycle alert if cycles detected
        if (cycle_detected) {
            this.cycleAlert.classList.remove('hidden');
            this.displayCycles(cycles);
        } else {
            this.cycleAlert.classList.add('hidden');
            this.cyclesSection.classList.add('hidden');
        }

        // Render dependency graph
        if (tasks.length > 0) {
            this.graphSection.classList.remove('hidden');
            // Rebuild task list with original dependencies for graph
            const tasksWithDeps = this.tasks.map(t => ({
                ...t,
                id: t.id,
                title: t.title,
                dependencies: t.dependencies || []
            }));
            this.renderDependencyGraph(tasksWithDeps, cycles);
            
            // Render Eisenhower matrix
            this.renderEisenhowerMatrix(tasks);
        }

        // Display tasks
        this.resultsList.innerHTML = tasks.map((task, index) => {
            const priorityLevel = this.getPriorityLevel(task.score);
            return `
                <div class="task-result-item ${priorityLevel}">
                    <div class="task-header">
                        <div class="task-title-section">
                            <div class="task-rank">${index + 1}</div>
                            <div>
                                <div class="task-title">${this.escapeHtml(task.title)}</div>
                                <div class="task-score">
                                    <span class="score-badge">${task.score.toFixed(2)} Score</span>
                                    <span class="priority-indicator ${priorityLevel}"></span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="task-details">
                        <div class="task-detail-item">
                            <div class="detail-label">Priority</div>
                            <div class="detail-value">${task.priority}/10</div>
                        </div>
                        <div class="task-detail-item">
                            <div class="detail-label">Effort</div>
                            <div class="detail-value">${task.effort}/10</div>
                        </div>
                        <div class="task-detail-item">
                            <div class="detail-label">Due Date</div>
                            <div class="detail-value">${task.due_date ? this.formatDate(task.due_date) : 'Not set'}</div>
                        </div>
                    </div>

                    <div class="components-chart">
                        <div class="component-bar">
                            <div class="component-label">Urgency</div>
                            <div class="component-bar-container">
                                <div class="component-bar-fill" style="width: ${task.components.urgency * 100}%">
                                    ${(task.components.urgency * 100).toFixed(0)}%
                                </div>
                            </div>
                        </div>
                        <div class="component-bar">
                            <div class="component-label">Importance</div>
                            <div class="component-bar-container">
                                <div class="component-bar-fill" style="width: ${task.components.importance_norm * 100}%">
                                    ${(task.components.importance_norm * 100).toFixed(0)}%
                                </div>
                            </div>
                        </div>
                        <div class="component-bar">
                            <div class="component-label">Effort Score</div>
                            <div class="component-bar-container">
                                <div class="component-bar-fill" style="width: ${task.components.effort * 100}%">
                                    ${(task.components.effort * 100).toFixed(0)}%
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="task-why">
                        <strong>Why this rank?</strong> This task scores high due to a combination of factors: 
                        ${this.generateExplanation(task, this.currentStrategy)}
                    </div>
                </div>
            `;
        }).join('');
    }

    displayCycles(cycles) {
        this.cyclesSection.classList.remove('hidden');
        this.cyclesList.innerHTML = cycles.map(cycle => {
            const cycleStr = cycle.join(' → ');
            return `<div class="cycle-item">🔄 ${cycleStr}</div>`;
        }).join('');
    }

    // ============================================
    // Dependency Graph Visualization
    // ============================================

    renderDependencyGraph(tasks, cycles) {
        const svg = this.depGraph;
        svg.innerHTML = ''; // Clear previous

        if (tasks.length === 0) return;

        const padding = 40;
        const width = svg.clientWidth || 600;
        const height = 400;
        const nodeRadius = 25;

        // Position nodes in a circle
        const positions = {};
        const angleSlice = (Math.PI * 2) / tasks.length;
        const centerX = width / 2;
        const centerY = height / 2;
        const radius = Math.min(width, height) / 2.5;

        tasks.forEach((task, i) => {
            const angle = angleSlice * i;
            positions[task.id] = {
                x: centerX + radius * Math.cos(angle),
                y: centerY + radius * Math.sin(angle)
            };
        });

        // Draw edges (dependencies)
        const cycleTaskIds = new Set(cycles.flat());
        tasks.forEach(task => {
            if (task.dependencies && Array.isArray(task.dependencies)) {
                task.dependencies.forEach(depId => {
                    const fromPos = positions[task.id];
                    const toPos = positions[depId];
                    if (fromPos && toPos) {
                        const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
                        line.setAttribute('x1', fromPos.x);
                        line.setAttribute('y1', fromPos.y);
                        line.setAttribute('x2', toPos.x);
                        line.setAttribute('y2', toPos.y);
                        line.setAttribute('stroke', cycleTaskIds.has(task.id) || cycleTaskIds.has(depId) ? '#ef4444' : '#d1d5db');
                        line.setAttribute('stroke-width', '2');
                        line.setAttribute('marker-end', cycleTaskIds.has(task.id) || cycleTaskIds.has(depId) ? 'url(#arrowred)' : 'url(#arrowgray)');
                        svg.appendChild(line);
                    }
                });
            }
        });

        // Arrow markers
        const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
        const markerGray = document.createElementNS('http://www.w3.org/2000/svg', 'marker');
        markerGray.setAttribute('id', 'arrowgray');
        markerGray.setAttribute('markerWidth', '10');
        markerGray.setAttribute('markerHeight', '10');
        markerGray.setAttribute('refX', '9');
        markerGray.setAttribute('refY', '3');
        markerGray.setAttribute('orient', 'auto');
        markerGray.innerHTML = '<polygon points="0 0, 10 3, 0 6" fill="#d1d5db" />';
        defs.appendChild(markerGray);

        const markerRed = document.createElementNS('http://www.w3.org/2000/svg', 'marker');
        markerRed.setAttribute('id', 'arrowred');
        markerRed.setAttribute('markerWidth', '10');
        markerRed.setAttribute('markerHeight', '10');
        markerRed.setAttribute('refX', '9');
        markerRed.setAttribute('refY', '3');
        markerRed.setAttribute('orient', 'auto');
        markerRed.innerHTML = '<polygon points="0 0, 10 3, 0 6" fill="#ef4444" />';
        defs.appendChild(markerRed);
        svg.appendChild(defs);

        // Draw nodes
        tasks.forEach(task => {
            const pos = positions[task.id];
            const isInCycle = cycleTaskIds.has(task.id);

            const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            circle.setAttribute('cx', pos.x);
            circle.setAttribute('cy', pos.y);
            circle.setAttribute('r', nodeRadius);
            circle.setAttribute('class', 'graph-node-circle ' + (isInCycle ? 'cycle' : ''));
            circle.setAttribute('stroke', isInCycle ? '#ef4444' : '#6366f1');
            circle.setAttribute('fill', isInCycle ? '#fecaca' : 'white');
            svg.appendChild(circle);

            const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            text.setAttribute('x', pos.x);
            text.setAttribute('y', pos.y + 4);
            text.setAttribute('class', 'graph-node-text');
            text.setAttribute('font-weight', 'bold');
            const label = task.title.split(' ')[0].substring(0, 4);
            text.textContent = label;
            svg.appendChild(text);
        });
    }

    // ============================================
    // Eisenhower Matrix Visualization
    // ============================================

    renderEisenhowerMatrix(tasks) {
        // Clear quadrants
        [this.q1, this.q2, this.q3, this.q4].forEach(q => q.innerHTML = '');

        tasks.forEach(task => {
            const urgency = task.components.urgency;
            const importance = task.components.importance_norm;

            // Determine quadrant (using 0.5 as threshold for each axis)
            let quadrant;
            if (urgency >= 0.5 && importance >= 0.5) {
                quadrant = 0; // Q1: Do First
            } else if (urgency < 0.5 && importance >= 0.5) {
                quadrant = 1; // Q2: Schedule
            } else if (urgency >= 0.5 && importance < 0.5) {
                quadrant = 2; // Q3: Delegate
            } else {
                quadrant = 3; // Q4: Eliminate
            }

            const quadrants = [this.q1, this.q2, this.q3, this.q4];
            const taskItem = document.createElement('div');
            taskItem.className = 'quadrant-task-item';
            taskItem.innerHTML = `
                <div class="quadrant-task-title">${this.escapeHtml(task.title)}</div>
                <div class="quadrant-task-score">Score: ${task.score.toFixed(2)} | U: ${(urgency * 100).toFixed(0)}% I: ${(importance * 100).toFixed(0)}%</div>
            `;
            quadrants[quadrant].appendChild(taskItem);
        });

        this.eisenhowerSection.classList.remove('hidden');
    }

    generateExplanation(task, strategy) {
        const components = task.components;
        const reasons = [];

        if (components.urgency >= 0.7) {
            reasons.push('approaching deadline');
        }
        if (components.importance_norm >= 0.7) {
            reasons.push('high importance');
        }
        if (components.effort >= 0.5) {
            reasons.push('good effort-to-value ratio');
        }

        if (reasons.length === 0) {
            reasons.push('overall balance of all factors');
        }

        return reasons.join(', ') + '.';
    }

    updateStrategyInfo() {
        const strategyDescriptions = {
            smart: '🧠 Smart Balance - Combines urgency (40%), importance (40%), and effort efficiency (20%)',
            effort: '⚡ Fastest Wins - Prioritizes tasks with lowest effort to build momentum',
            importance: '🎯 High Impact - Focuses on task importance regardless of effort or urgency',
            urgency: '⏰ Deadline Driven - Prioritizes tasks by urgency and approaching deadlines'
        };
        this.strategyInfo.textContent = strategyDescriptions[this.currentStrategy];
    }

    getPriorityLevel(score) {
        if (score >= 0.7) return 'high';
        if (score >= 0.4) return 'medium';
        return 'low';
    }

    formatDate(dateString) {
        if (!dateString) return 'Not set';
        const options = { year: 'numeric', month: 'short', day: 'numeric' };
        return new Date(dateString).toLocaleDateString('en-US', options);
    }

    // ============================================
    // UI State Management
    // ============================================

    showLoading() {
        this.emptyState.classList.add('hidden');
        this.resultsContainer.classList.add('hidden');
        this.errorState.classList.add('hidden');
        this.loadingState.classList.remove('hidden');
    }

    hideLoading() {
        this.loadingState.classList.add('hidden');
    }

    showResults() {
        this.emptyState.classList.add('hidden');
        this.errorState.classList.add('hidden');
        this.resultsContainer.classList.remove('hidden');
    }

    hideResults() {
        this.resultsContainer.classList.add('hidden');
        this.emptyState.classList.remove('hidden');
    }

    showError(message) {
        this.errorMessage.textContent = message;
        this.errorState.classList.remove('hidden');
        this.loadingState.classList.add('hidden');
        setTimeout(() => {
            this.errorState.classList.add('hidden');
        }, 5000);
    }

    showSuccess(message) {
        // Simple toast notification (can be enhanced)
        console.log('✓ ' + message);
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // ============================================
    // Local Storage
    // ============================================

    saveToLocalStorage() {
        localStorage.setItem('taskAnalyzerTasks', JSON.stringify(this.tasks));
    }

    loadFromLocalStorage() {
        const stored = localStorage.getItem('taskAnalyzerTasks');
        if (stored) {
            this.tasks = JSON.parse(stored);
            this.updateTasksPreview();
        }
    }

    // ============================================
    // Feedback & Learning System
    // ============================================

    loadFeedbackStats() {
        const stored = localStorage.getItem('taskAnalyzerFeedback');
        if (stored) {
            this.feedbackStats = JSON.parse(stored);
        }
    }

    saveFeedbackStats() {
        localStorage.setItem('taskAnalyzerFeedback', JSON.stringify(this.feedbackStats));
    }

    recordFeedback(taskId, helpful) {
        if (!this.feedbackStats[taskId]) {
            this.feedbackStats[taskId] = { helpful: 0, unhelpful: 0 };
        }
        if (helpful) {
            this.feedbackStats[taskId].helpful++;
        } else {
            this.feedbackStats[taskId].unhelpful++;
        }
        this.saveFeedbackStats();
        console.log('Feedback recorded for', taskId, helpful ? '👍' : '👎');
    }

    getFeedbackBadge(taskId) {
        const stats = this.feedbackStats[taskId];
        if (!stats) return '';
        const total = stats.helpful + stats.unhelpful;
        if (total === 0) return '';
        const helpfulPct = ((stats.helpful / total) * 100).toFixed(0);
        return ` <span class="feedback-badge">${stats.helpful}👍 ${stats.unhelpful}👎</span>`;
    }
}

// ============================================
// Initialize Application
// ============================================

let app;

document.addEventListener('DOMContentLoaded', () => {
    app = new TaskAnalyzer();
    console.log('Task Analyzer initialized');
});
