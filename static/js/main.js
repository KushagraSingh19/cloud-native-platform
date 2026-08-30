/**
 * Cloud Task Manager - Frontend Client Application
 * Communicates with Flask REST API using JavaScript fetch() API.
 */

document.addEventListener("DOMContentLoaded", () => {
    // DOM Elements
    const healthBadge = document.getElementById("healthBadge");
    const healthText = document.getElementById("healthText");
    const addTaskForm = document.getElementById("addTaskForm");
    const taskTitleInput = document.getElementById("taskTitleInput");
    const taskList = document.getElementById("taskList");
    const emptyState = document.getElementById("emptyState");
    const filterCount = document.getElementById("filterCount");
    const filterBtns = document.querySelectorAll(".filter-btn");

    // Metrics Elements
    const totalTasksCount = document.getElementById("totalTasksCount");
    const pendingTasksCount = document.getElementById("pendingTasksCount");
    const completedTasksCount = document.getElementById("completedTasksCount");

    // State Variables
    let tasks = [];
    let currentFilter = "all";

    // -------------------------------------------------------------------------
    // Health Check Status
    // -------------------------------------------------------------------------
    async function checkHealth() {
        try {
            const response = await fetch("/health");
            if (response.ok) {
                const data = await response.json();
                if (data.status === "healthy") {
                    healthBadge.className = "health-badge healthy";
                    healthText.textContent = "API Healthy";
                } else {
                    healthBadge.className = "health-badge unhealthy";
                    healthText.textContent = "API Unhealthy";
                }
            } else {
                healthBadge.className = "health-badge unhealthy";
                healthText.textContent = "Health Alert";
            }
        } catch (error) {
            console.error("Health check error:", error);
            healthBadge.className = "health-badge unhealthy";
            healthText.textContent = "Offline";
        }
    }

    // -------------------------------------------------------------------------
    // REST API Calls
    // -------------------------------------------------------------------------

    // Fetch all tasks from GET /api/tasks
    async function fetchTasks() {
        try {
            const response = await fetch("/api/tasks");
            if (!response.ok) {
                throw new Error("Failed to fetch tasks");
            }
            tasks = await response.json();
            renderTasks();
            updateMetrics();
        } catch (error) {
            console.error("Error fetching tasks:", error);
            showToast("Error loading tasks", "error");
        }
    }

    // Create task via POST /api/tasks
    async function addTask(title) {
        try {
            const response = await fetch("/api/tasks", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ title: title })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || "Failed to create task");
            }

            const new_task = await response.json();
            tasks.push(new_task);
            taskTitleInput.value = "";
            renderTasks();
            updateMetrics();
            showToast("Task added successfully", "success");
        } catch (error) {
            console.error("Error adding task:", error);
            showToast(error.message, "error");
        }
    }

    // Toggle completion status via PUT /api/tasks/<id>
    async function toggleTask(id, completedStatus) {
        try {
            const response = await fetch(`/api/tasks/${id}`, {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ completed: completedStatus })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || "Failed to update task");
            }

            const updatedTask = await response.json();
            const index = tasks.findIndex(t => t.id === id);
            if (index !== -1) {
                tasks[index] = updatedTask;
            }

            renderTasks();
            updateMetrics();
            showToast(completedStatus ? "Task completed" : "Task marked pending", "success");
        } catch (error) {
            console.error("Error toggling task:", error);
            showToast(error.message, "error");
        }
    }

    // Delete task via DELETE /api/tasks/<id>
    async function deleteTask(id) {
        try {
            const response = await fetch(`/api/tasks/${id}`, {
                method: "DELETE"
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || "Failed to delete task");
            }

            tasks = tasks.filter(t => t.id !== id);
            renderTasks();
            updateMetrics();
            showToast("Task deleted", "success");
        } catch (error) {
            console.error("Error deleting task:", error);
            showToast(error.message, "error");
        }
    }

    // -------------------------------------------------------------------------
    // UI Rendering & Event Handlers
    // -------------------------------------------------------------------------

    function renderTasks() {
        taskList.innerHTML = "";

        const filteredTasks = tasks.filter(task => {
            if (currentFilter === "pending") return !task.completed;
            if (currentFilter === "completed") return task.completed;
            return true;
        });

        filterCount.textContent = `${filteredTasks.length} item${filteredTasks.length === 1 ? "" : "s"}`;

        if (filteredTasks.length === 0) {
            emptyState.classList.remove("hidden");
        } else {
            emptyState.classList.add("hidden");
            filteredTasks.forEach(task => {
                const li = document.createElement("li");
                li.className = `task-item ${task.completed ? "completed" : ""}`;
                
                li.innerHTML = `
                    <div class="task-left">
                        <input 
                            type="checkbox" 
                            class="custom-checkbox" 
                            ${task.completed ? "checked" : ""}
                            data-id="${task.id}"
                        />
                        <div class="task-details">
                            <span class="task-title">${escapeHtml(task.title)}</span>
                            <span class="task-meta"><i class="fa-regular fa-clock"></i> Created ${task.created_at}</span>
                        </div>
                    </div>
                    <div class="task-actions">
                        <button class="btn-icon delete-btn" data-id="${task.id}" title="Delete Task">
                            <i class="fa-regular fa-trash-can"></i>
                        </button>
                    </div>
                `;

                // Add event listeners for checkbox & delete button
                const checkbox = li.querySelector(".custom-checkbox");
                checkbox.addEventListener("change", (e) => {
                    toggleTask(task.id, e.target.checked);
                });

                const deleteBtn = li.querySelector(".delete-btn");
                deleteBtn.addEventListener("click", () => {
                    deleteTask(task.id);
                });

                taskList.appendChild(li);
            });
        }
    }

    function updateMetrics() {
        const total = tasks.length;
        const completed = tasks.filter(t => t.completed).length;
        const pending = total - completed;

        totalTasksCount.textContent = total;
        pendingTasksCount.textContent = pending;
        completedTasksCount.textContent = completed;
    }

    // Handle Form Submit
    addTaskForm.addEventListener("submit", (e) => {
        e.preventDefault();
        const title = taskTitleInput.value.trim();
        if (title) {
            addTask(title);
        }
    });

    // Handle Filter Buttons
    filterBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            filterBtns.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            currentFilter = btn.dataset.filter;
            renderTasks();
        });
    });

    // Toast Notification Helper
    function showToast(message, type = "success") {
        const toastContainer = document.getElementById("toastContainer");
        const toast = document.createElement("div");
        toast.className = `toast ${type}`;
        
        const iconClass = type === "success" ? "fa-solid fa-circle-check" : "fa-solid fa-circle-exclamation";
        toast.innerHTML = `<i class="${iconClass}"></i> <span>${escapeHtml(message)}</span>`;
        
        toastContainer.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = "0";
            toast.style.transform = "translateY(10px)";
            toast.style.transition = "all 0.3s ease";
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    // Helper to sanitize HTML text
    function escapeHtml(text) {
        const div = document.createElement("div");
        div.textContent = text;
        return div.innerHTML;
    }

    // Initial Load
    checkHealth();
    fetchTasks();
});
