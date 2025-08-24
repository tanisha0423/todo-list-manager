import json
from datetime import datetime, timedelta
import os

# File where all tasks will be saved
TASKS_FILE = "tasks.json"

# ----------------- Utility Functions -----------------
def load_tasks():
    """
    Load tasks from the JSON file.
    If the file doesn't exist or is empty, return an empty list.
    """
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, "r") as file:
            try:
                return json.load(file)  # Load tasks if valid JSON
            except json.JSONDecodeError:
                return []  # Return empty list if file is corrupted/empty
    return []


def save_tasks(tasks):
    """
    Save all tasks into the JSON file so they are not lost when program exits.
    """
    with open(TASKS_FILE, "w") as file:
        json.dump(tasks, file, indent=4)  # Save tasks in pretty format


def get_due_date():
    """
    Ask the user for a due date in YYYY-MM-DD format.
    User can press Enter to skip setting a due date.
    Keeps asking until a valid date is entered.
    """
    while True:
        date_input = input("Enter due date (YYYY-MM-DD) or press Enter to skip: ").strip()
        if not date_input:  # If user skips
            return None
        try:
            datetime.strptime(date_input, "%Y-%m-%d")  # Validate date format
            return date_input
        except ValueError:
            print("❌ Invalid date format. Use YYYY-MM-DD.")


def get_priority():
    """
    Ask the user for task priority (low/medium/high).
    Default is 'medium'.
    Keeps asking until valid input is given.
    """
    while True:
        priority = input("Enter priority (low/medium/high) [default=medium]: ").strip().lower() or "medium"
        if priority in ["low", "medium", "high"]:
            return priority
        print("❌ Invalid priority. Choose from low, medium, or high.")


# ----------------- Task Operations -----------------
def add_task(tasks):
    """
    Add a new task with description, optional due date, and priority.
    Task status is set to 'pending' by default.
    """
    description = input("Enter task description: ").strip()
    due_date = get_due_date()
    priority = get_priority()

    task = {
        "description": description,
        "due_date": due_date,
        "status": "pending",
        "priority": priority
    }
    tasks.append(task)
    save_tasks(tasks)  # Save immediately so nothing is lost
    print("✅ Task added successfully!")


def view_tasks(tasks, filter_mode="all", return_filtered=False):
    """
    Display tasks based on filter mode:
    - all: show every task
    - completed: show only completed tasks
    - pending: show only tasks not completed
    - due_soon: show tasks due within 3 days
    Returns visible task list if return_filtered=True (useful for editing/deleting).
    """
    if not tasks:
        print("No tasks found.")
        return [] if return_filtered else None

    print("\n--- TASK LIST ---")
    today = datetime.today()
    visible_tasks = []

    for task in tasks:
        due = task["due_date"]
        status = task["status"]

        # Apply filter conditions
        if filter_mode == "completed" and status != "completed":
            continue
        elif filter_mode == "pending" and status != "pending":
            continue
        elif filter_mode == "due_soon":
            if due:
                due_date_obj = datetime.strptime(due, "%Y-%m-%d")
                if due_date_obj > today + timedelta(days=3):
                    continue
            else:
                continue

        visible_tasks.append(task)

    # If nothing matched the filter
    if not visible_tasks:
        print("No tasks match this filter.")
        return [] if return_filtered else None

    # Nicely print each task
    for i, task in enumerate(visible_tasks, start=1):
        due = task["due_date"]
        status = task["status"]
        priority = task.get("priority", "medium")

        # Add warning notes for overdue or soon-to-due tasks
        status_note = ""
        if due:
            due_date_obj = datetime.strptime(due, "%Y-%m-%d")
            if due_date_obj < today:
                status_note = "⚠️ OVERDUE!"
            elif due_date_obj <= today + timedelta(days=3):
                status_note = "⏳ Due Soon"

        print(f"{i}. {task['description']} | Due: {due or 'N/A'} | "
              f"Status: {status} {status_note} | Priority: {priority}")

    print("-----------------")
    return visible_tasks if return_filtered else None


def mark_completed(tasks):
    """
    Let user choose a task from pending tasks and mark it as completed.
    """
    visible = view_tasks(tasks, "pending", return_filtered=True)
    if not visible:
        return
    try:
        idx = int(input("Enter task number to mark as completed: ")) - 1
        if 0 <= idx < len(visible):
            task = visible[idx]
            task["status"] = "completed"
            save_tasks(tasks)
            print("✅ Task marked as completed.")
        else:
            print("❌ Invalid task number.")
    except ValueError:
        print("❌ Please enter a valid number.")


def edit_task(tasks):
    """
    Edit a task's description, due date, or priority.
    User can skip fields to keep them unchanged.
    """
    visible = view_tasks(tasks, return_filtered=True)
    if not visible:
        return
    try:
        idx = int(input("Enter task number to edit: ")) - 1
        if 0 <= idx < len(visible):
            task = visible[idx]
            new_desc = input("Enter new description (leave blank to keep current): ").strip()
            new_due = get_due_date()
            new_priority = input("Enter new priority (low/medium/high or Enter to skip): ").strip().lower()

            if new_desc:
                task["description"] = new_desc
            if new_due:
                task["due_date"] = new_due
            if new_priority in ["low", "medium", "high"]:
                task["priority"] = new_priority

            save_tasks(tasks)
            print("✅ Task updated.")
        else:
            print("❌ Invalid task number.")
    except ValueError:
        print("❌ Please enter a valid number.")


def delete_task(tasks):
    """
    Delete a task from the list after confirming with the user.
    """
    visible = view_tasks(tasks, return_filtered=True)
    if not visible:
        return
    try:
        idx = int(input("Enter task number to delete: ")) - 1
        if 0 <= idx < len(visible):
            removed = visible[idx]
            confirm = input(f"Are you sure you want to delete '{removed['description']}'? (y/n): ").lower()
            if confirm == "y":
                tasks.remove(removed)
                save_tasks(tasks)
                print(f"🗑️ Task '{removed['description']}' deleted.")
            else:
                print("❌ Deletion cancelled.")
        else:
            print("❌ Invalid task number.")
    except ValueError:
        print("❌ Please enter a valid number.")


# ----------------- Main Menu -----------------
def main():
    """
    Main menu loop that runs the To-Do List Manager.
    Keeps running until user chooses to exit.
    """
    tasks = load_tasks()

    while True:
        print("\n====== To-Do List Manager ======")
        print("1. Add Task")
        print("2. View All Tasks")
        print("3. View Completed Tasks")
        print("4. View Pending Tasks")
        print("5. View Tasks Due Soon")
        print("6. Mark Task as Completed")
        print("7. Edit Task")
        print("8. Delete Task")
        print("9. Exit")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            add_task(tasks)
        elif choice == "2":
            view_tasks(tasks, "all")
        elif choice == "3":
            view_tasks(tasks, "completed")
        elif choice == "4":
            view_tasks(tasks, "pending")
        elif choice == "5":
            view_tasks(tasks, "due_soon")
        elif choice == "6":
            mark_completed(tasks)
        elif choice == "7":
            edit_task(tasks)
        elif choice == "8":
            delete_task(tasks)
        elif choice == "9":
            print("👋 Exiting To-Do List Manager. Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
