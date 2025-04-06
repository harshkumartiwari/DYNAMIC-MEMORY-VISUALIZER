import tkinter as tk
from tkinter import scrolledtext, simpledialog, messagebox
import random

class MemoryBlock:
    def __init__(self, start_address, size, is_allocated=False, process_id=None):
        self.start_address = start_address
        self.size = size
        self.is_allocated = is_allocated
        self.process_id = process_id

class MemoryVisualizer:
    def __init__(self, master, initial_memory_size):
        self.master = master
        master.title("Dynamic Memory Management Visualizer")
        self.memory_size = initial_memory_size
        self.memory = [MemoryBlock(0, self.memory_size)]  # Initially, the entire memory is free
        # --- Configuration ---
        self.canvas_width = 600
        self.canvas_height = 250
        self.allocated_color = "#ADD8E6"  # Light Blue (default if no PID)
        self.free_color = "#F0FFF0"      # Light Green
        self.border_color = "black"
        self.fragmented_border_color = "red"
        self.external_fragmentation_color = "orange" # New color for external fragmentation
        self.text_color = "black"
        self.padding = 5
        self.process_colors = {} # Dictionary to store PID and its color
        self.next_color_index = 0
        self.available_colors = ["#FFDAB9", "#E6E6FA", "#AFEEEE", "#F08080", "#98FB98", "#DDA0DD", "#B0E0E6", "#FFA07A"] # Some example colors
        self.algorithm_var = tk.StringVar(master)
        self.algorithm_var.set("First-Fit")  # Default algorithm
        self.last_allocated_index_next_fit = 0 # For Next-Fit algorithm
        # --- Main Canvas ---
        self.canvas = tk.Canvas(master, width=self.canvas_width, height=self.canvas_height, bg="white", bd=2, relief=tk.SUNKEN)
        self.canvas.grid(row=0, column=0, columnspan=2, padx=self.padding, pady=self.padding, sticky="ew")
        # --- Control Frame ---
        controls_frame = tk.Frame(master)
        controls_frame.grid(row=1, column=0, padx=self.padding, pady=self.padding, sticky="ew")
        # Allocation Controls
        allocation_frame = tk.LabelFrame(controls_frame, text="Allocation", padx=self.padding, pady=self.padding)
        allocation_frame.pack(side=tk.LEFT, fill="x", expand=True)
        tk.Label(allocation_frame, text="Size:").grid(row=0, column=0, sticky="w")
        self.allocation_entry = tk.Entry(allocation_frame, width=10)
        self.allocation_entry.grid(row=0, column=1)
        tk.Label(allocation_frame, text="PID (optional):").grid(row=1, column=0, sticky="w")
        self.process_id_entry = tk.Entry(allocation_frame, width=5)
        self.process_id_entry.grid(row=1, column=1)
        self.allocate_button = tk.Button(allocation_frame, text="Allocate", command=self.allocate_memory)
        self.allocate_button.grid(row=0, column=2, rowspan=2, padx=self.padding)
        # Deallocation Controls
        deallocation_frame = tk.LabelFrame(controls_frame, text="Deallocation", padx=self.padding, pady=self.padding)
        deallocation_frame.pack(side=tk.LEFT, fill="x", expand=True)
        tk.Label(deallocation_frame, text="Address:").grid(row=0, column=0, sticky="w")
        self.deallocation_entry = tk.Entry(deallocation_frame, width=10)
        self.deallocation_entry.grid(row=0, column=1)
        self.deallocate_button = tk.Button(deallocation_frame, text="Deallocate", command=self.deallocate_memory)
        self.deallocate_button.grid(row=0, column=2, padx=self.padding)
        # --- Algorithm Selection Frame ---
        algorithm_frame = tk.LabelFrame(master, text="Algorithm Selection", padx=self.padding, pady=self.padding)
        algorithm_frame.grid(row=1, column=1, padx=self.padding, pady=self.padding, sticky="ew")
        tk.Label(algorithm_frame, text="Choose Algorithm:").pack()
        algorithms = ["First-Fit", "Best-Fit", "Worst-Fit", "Next-Fit"]
        self.algorithm_menu = tk.OptionMenu(algorithm_frame, self.algorithm_var, *algorithms, command=self.update_algorithm_display)
        self.algorithm_menu.pack()
        self.algorithm_display_label = tk.Label(algorithm_frame, text=f"Current: {self.algorithm_var.get()}")
        self.algorithm_display_label.pack()
        # --- Information Display Frame ---
        info_frame = tk.LabelFrame(master, text="Memory Information", padx=self.padding, pady=self.padding)
        info_frame.grid(row=2, column=0, columnspan=2, padx=self.padding, pady=self.padding, sticky="ew")
        self.total_memory_label = tk.Label(info_frame, text=f"Total Memory: {self.memory_size}")
        self.total_memory_label.pack(side=tk.LEFT, padx=self.padding)
        self.free_blocks_label = tk.Label(info_frame, text="Free Blocks: 1") # Initial state
        self.free_blocks_label.pack(side=tk.LEFT, padx=self.padding)
        self.free_memory_label = tk.Label(info_frame, text=f"Free Memory: {self.memory_size}") # Initial state
        self.free_memory_label.pack(side=tk.LEFT, padx=self.padding)
        self.allocated_memory_label = tk.Label(info_frame, text="Allocated Memory: 0") # New label
        self.allocated_memory_label.pack(side=tk.LEFT, padx=self.padding)
        self.internal_fragmentation_label = tk.Label(info_frame, text="Internal Fragmentation: 0") # New label
        self.internal_fragmentation_label.pack(side=tk.LEFT, padx=self.padding)
        # --- Reset Button ---
        reset_button = tk.Button(info_frame, text="Reset Memory", command=self.reset_memory)
        reset_button.pack(side=tk.RIGHT, padx=self.padding)
        # --- Memory Map ---
        memory_map_frame = tk.LabelFrame(master, text="Memory Map", padx=self.padding, pady=self.padding)
        memory_map_frame.grid(row=3, column=0, columnspan=2, padx=self.padding, pady=self.padding, sticky="ew")
        self.memory_map_text = scrolledtext.ScrolledText(memory_map_frame, height=10, width=70)
        self.memory_map_text.pack()
        self.update_memory_map()
        self.draw_memory()
        self.update_free_block_count()
        self.update_fragmentation_info()
        self.update_allocated_memory_info()
        self.update_internal_fragmentation_info()

    def update_free_block_count(self):
        free_count = sum(1 for block in self.memory if not block.is_allocated)
        self.free_blocks_label.config(text=f"Free Blocks: {free_count}")

    def update_algorithm_display(self, algorithm):
        self.algorithm_display_label.config(text=f"Current: {algorithm}")

    def draw_memory(self):
        self.canvas.delete("all")
        y_start = 50
        block_height = 50
        padding = 5
        for i, block in enumerate(self.memory):
            x1 = (block.start_address / self.memory_size) * (self.canvas_width - 2 * self.padding) + self.padding
            x2 = ((block.start_address + block.size) / self.memory_size) * (self.canvas_width - 2 * self.padding) + self.padding
            y1 = y_start + padding
            y2 = y_start + block_height - padding
            outline_color = self.border_color # Default border color

            if block.is_allocated:
                fill_color = self.process_colors.get(block.process_id) or self.allocated_color
                text = f"Addr: {block.start_address}\nSize: {block.size}"
                if block.process_id:
                    text += f"\nPID: {block.process_id}"
            else:
                fill_color = self.free_color
                # Highlight fragmented free blocks (internal fragmentation handled in info label)
                is_externally_fragmented = True
                if i > 0 and not self.memory[i-1].is_allocated:
                    is_externally_fragmented = False
                if i < len(self.memory) - 1 and not self.memory[i+1].is_allocated:
                    is_externally_fragmented = False
                if is_externally_fragmented and block.size < self.memory_size: # Avoid highlighting the initial free block
                    outline_color = self.external_fragmentation_color
                else:
                    outline_color = self.border_color

                text = f"Addr: {block.start_address}\nSize: {block.size}"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill_color, outline=outline_color, width=2)
                text_x = (x1 + x2) / 2
                text_y = (y1 + y2) / 2
                self.canvas.create_text(text_x, text_y, text=text, fill=self.text_color, justify=tk.CENTER)
                continue # Skip the rest for free blocks

            self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill_color, outline=outline_color, width=2)
            text_x = (x1 + x2) / 2
            text_y = (y1 + y2) / 2
            self.canvas.create_text(text_x, text_y, text=text, fill=self.text_color, justify=tk.CENTER)
            y_start += block_height + padding // 2 # Add a small gap between blocks

    def allocate_memory(self):
        size_str = self.allocation_entry.get()
        process_id = self.process_id_entry.get()
        try:
            size = int(size_str)
            if size > 0:
                algorithm = self.algorithm_var.get()
                free_blocks = [(i, block) for i, block in enumerate(self.memory) if not block.is_allocated and block.size >= size]
                if not free_blocks:
                    messagebox.showinfo("Allocation Failed", "Not enough contiguous memory available.")
                    return

                best_block_index = -1

                if algorithm == "First-Fit":
                    best_block_index = free_blocks[0][0] if free_blocks else -1
                elif algorithm == "Best-Fit":
                    best_block_index = min(free_blocks, key=lambda item: item[1].size)[0] if free_blocks else -1
                elif algorithm == "Worst-Fit":
                    best_block_index = max(free_blocks, key=lambda item: item[1].size)[0] if free_blocks else -1
                elif algorithm == "Next-Fit":
                    start_index = self.last_allocated_index_next_fit
                    found = False
                    for i in range(len(free_blocks)):
                        index_in_memory = free_blocks[(start_index + i) % len(free_blocks)][0]
                        if self.memory[index_in_memory].size >= size:
                            best_block_index = index_in_memory
                            self.last_allocated_index_next_fit = (start_index + i + 1) % len(free_blocks) if free_blocks else 0
                            found = True
                            break
                    if not found and free_blocks:
                        # Search from the beginning up to the original start index
                        for i in range(start_index):
                            index_in_memory = free_blocks[i][0]
                            if self.memory[index_in_memory].size >= size:
                                best_block_index = index_in_memory
                                self.last_allocated_index_next_fit = i + 1 if i + 1 < len(free_blocks) else 0
                                found = True
                                break
                    if not found:
                        best_block_index = -1

                if best_block_index != -1:
                    # Find the index of the free block in the self.memory list
                    memory_index = -1
                    for i, block in enumerate(self.memory):
                        if not block.is_allocated and block.start_address == self.memory[best_block_index].start_address and block.size == self.memory[best_block_index].size:
                            memory_index = i
                            break

                    if memory_index != -1:
                        best_block = self.memory[memory_index]
                        start_address = best_block.start_address
                        allocated_pid = process_id if process_id else None
                        if allocated_pid and allocated_pid not in self.process_colors:
                            self.process_colors[allocated_pid] = self.available_colors[self.next_color_index % len(self.available_colors)]
                            self.next_color_index += 1
                        if best_block.size == size:
                            self.memory[memory_index].is_allocated = True
                            self.memory[memory_index].process_id = allocated_pid
                        else:
                            allocated_block = MemoryBlock(start_address, size, True, allocated_pid)
                            remaining_block = MemoryBlock(start_address + size, best_block.size - size)
                            self.memory.pop(memory_index)
                            self.memory.insert(memory_index, allocated_block)
                            self.memory.insert(memory_index + 1, remaining_block)
                        self.draw_memory()
                        self.update_free_block_count()
                        self.update_fragmentation_info()
                        self.update_allocated_memory_info()
                        self.update_internal_fragmentation_info()
                        self.update_memory_map()
                    else:
                        messagebox.showinfo("Allocation Error", "Error finding the free block in memory.")
                else:
                    messagebox.showinfo("Allocation Failed", f"No suitable free block found using {algorithm} algorithm.")
            else:
                messagebox.showerror("Invalid Input", "Allocation size must be a positive integer.")
        except ValueError:
            messagebox.showerror("Invalid Input", "Invalid allocation size.")

    def deallocate_memory(self):
        address_str = self.deallocation_entry.get()
        try:
            address = int(address_str)
            deallocated = False
            for i, block in enumerate(self.memory):
                if block.start_address == address and block.is_allocated:
                    self.memory[i].is_allocated = False
                    self.memory[i].process_id = None
                    self.coalesce_memory()  # Try to merge adjacent free blocks
                    self.draw_memory()
                    self.update_free_block_count()
                    self.update_fragmentation_info()
                    self.update_allocated_memory_info()
                    self.update_internal_fragmentation_info()
                    self.update_memory_map()
                    deallocated = True
                    break
            if not deallocated:
                messagebox.showinfo("Deallocation Failed", f"No allocated block found at address {address}.")
        except ValueError:
            messagebox.showerror("Invalid Input", "Invalid address.")

    def coalesce_memory(self):
        self.memory.sort(key=lambda block: block.start_address)
        i = 0
        while i < len(self.memory) - 1:
            if not self.memory[i].is_allocated and not self.memory[i+1].is_allocated and \
               self.memory[i].start_address + self.memory[i].size == self.memory[i+1].start_address:
                self.memory[i].size += self.memory[i+1].size
                self.memory.pop(i+1)
            else:
                i += 1

    def reset_memory(self):
        """Resets the memory to its initial state (one large free block)."""
        self.memory = [MemoryBlock(0, self.memory_size)]
        self.process_colors = {}
        self.next_color_index = 0
        self.last_allocated_index_next_fit = 0
        self.draw_memory()
        self.update_free_block_count()
        self.update_fragmentation_info()
        self.update_allocated_memory_info()
        self.update_internal_fragmentation_info()
        self.update_memory_map()

    def update_fragmentation_info(self):
        """Calculates and updates the external fragmentation information display."""
        free_blocks = [block for block in self.memory if not block.is_allocated]
        if not free_blocks:
            self.free_memory_label.config(text="Free Memory: 0")
            return

        total_free_memory = sum(block.size for block in free_blocks)
        self.free_memory_label.config(text=f"Free Memory: {total_free_memory}")

    def update_allocated_memory_info(self):
        """Calculates and updates the allocated memory information display."""
        total_allocated_memory = sum(block.size for block in self.memory if block.is_allocated)
        self.allocated_memory_label.config(text=f"Allocated Memory: {total_allocated_memory}")

    def update_internal_fragmentation_info(self):
        """Calculates and updates the internal fragmentation information display."""
        # In this simplified model, we allocate exactly the requested size,
        # so internal fragmentation is always 0.
        # In a more realistic scenario, if a process is allocated a larger block,
        # the difference would be internal fragmentation.
        self.internal_fragmentation_label.config(text="Internal Fragmentation: 0")

    def update_memory_map(self):
        """Updates the memory map display."""
        self.memory_map_text.delete("1.0", tk.END)
        self.memory_map_text.insert(tk.END, "Address\tSize\tStatus\tPID\n")
        for block in self.memory:
            status = ""
            if block.is_allocated:
                status = "Allocated"
            else:
                status = "Free"
            pid_str = str(block.process_id) if block.process_id is not None else "-"
            self.memory_map_text.insert(tk.END, f"{block.start_address}\t{block.size}\t{status}\t{pid_str}\n")

if __name__ == "__main__":
    root = tk.Tk()
    initial_size = simpledialog.askinteger("Memory Size", "Enter the initial memory size:", initialvalue=500)
    if initial_size is not None and initial_size > 0:
        visualizer = MemoryVisualizer(root, initial_size)
        root.mainloop()
    else:
        messagebox.showerror("Error", "Invalid memory size. Application will close.")