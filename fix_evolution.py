"""Script to temporarily modify the memory system to disable evolution"""
import os
import sys

def disable_evolution():
    """Modify memory_system.py to disable memory evolution"""
    file_path = "memory_system.py"
    
    # Make backup
    with open(file_path, 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    with open(f"{file_path}.bak", 'w', encoding='utf-8') as f:
        f.write(original_content)
    
    # Find and replace the _process_memory_evolution method
    modified_content = original_content.replace(
        "    def _process_memory_evolution(self, note: MemoryNote) -> bool:",
        """    def _process_memory_evolution(self, note: MemoryNote) -> bool:
        # Temporarily disabled memory evolution
        print("Memory evolution disabled for debugging")
        return False"""
    )
    
    # Update the content with shorter version
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(modified_content)
    
    print("Memory evolution has been temporarily disabled")

def enable_evolution():
    """Restore the original memory_system.py"""
    file_path = "memory_system.py"
    backup_path = f"{file_path}.bak"
    
    if os.path.exists(backup_path):
        with open(backup_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(original_content)
        
        print("Memory evolution has been restored")
    else:
        print("No backup file found")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--restore":
        enable_evolution()
    else:
        disable_evolution()
