import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
from decimal import Decimal, getcontext

# For plotting inside Tkinter
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# Set the precision for the Decimal type to ensure it's our "ground truth"
getcontext().prec = 50

class FloatingPointErrorAnalyzer(tk.Tk):
    """
    A GUI application to demonstrate and analyze IEEE 754 floating-point rounding errors
    that occur during cumulative addition.
    """
    def __init__(self):
        super().__init__()
        self.title("IEEE 754 Floating-Point Error Analyzer")
        self.geometry("900x700")

        # --- Main frame ---
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Configure grid layout
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=2)
        main_frame.rowconfigure(5, weight=1) # Give weight to the plot row

        # --- Create widgets ---
        self._create_input_widgets(main_frame)
        self._create_results_display(main_frame)
        self._create_plot(main_frame)
        
        # Add a description label
        desc_label = ttk.Label(
            main_frame,
            text="This tool shows how adding a small number to a large number repeatedly causes rounding errors to accumulate.",
            justify=tk.CENTER,
            font=("Arial", 10, "italic")
        )
        desc_label.grid(row=0, column=0, columnspan=2, pady=(0, 15))


    def _create_input_widgets(self, parent):
        """Creates the input fields and the run button."""
        input_frame = ttk.LabelFrame(parent, text="Simulation Parameters", padding="10")
        input_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        input_frame.columnconfigure(1, weight=1)

        # Default values that clearly show the error for 32-bit floats
        self.large_num_var = tk.StringVar(value="10000000.0") # 1e7
        self.small_num_var = tk.StringVar(value="0.01")     # 1e-2
        self.iterations_var = tk.StringVar(value="100000")

        # Large Number
        ttk.Label(input_frame, text="Large Base Number:").grid(row=0, column=0, sticky="w", pady=2)
        ttk.Entry(input_frame, textvariable=self.large_num_var).grid(row=0, column=1, sticky="ew", pady=2)

        # Small Number
        ttk.Label(input_frame, text="Small Number to Add:").grid(row=1, column=0, sticky="w", pady=2)
        ttk.Entry(input_frame, textvariable=self.small_num_var).grid(row=1, column=1, sticky="ew", pady=2)

        # Iterations
        ttk.Label(input_frame, text="Number of Additions:").grid(row=2, column=0, sticky="w", pady=2)
        ttk.Entry(input_frame, textvariable=self.iterations_var).grid(row=2, column=1, sticky="ew", pady=2)

        # Precision
        ttk.Label(input_frame, text="Floating-Point Precision:").grid(row=3, column=0, sticky="w", pady=2)
        self.precision_var = tk.StringVar(value="Single (32-bit)")
        precision_menu = ttk.Combobox(
            input_frame,
            textvariable=self.precision_var,
            values=["Single (32-bit)", "Double (64-bit)"],
            state="readonly"
        )
        precision_menu.grid(row=3, column=1, sticky="ew", pady=2)

        # Run Button
        run_button = ttk.Button(input_frame, text="Run Analysis", command=self.run_analysis)
        run_button.grid(row=4, column=0, columnspan=2, pady=10)

    def _create_results_display(self, parent):
        """Creates the labels for displaying the calculation results."""
        results_frame = ttk.LabelFrame(parent, text="Results", padding="10")
        results_frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
        results_frame.columnconfigure(1, weight=1)
        
        self.expected_var = tk.StringVar(value="-")
        self.actual_var = tk.StringVar(value="-")
        self.abs_error_var = tk.StringVar(value="-")
        self.rel_error_var = tk.StringVar(value="-")

        # Expected Result
        ttk.Label(results_frame, text="Expected (Exact) Result:").grid(row=0, column=0, sticky="w", pady=3)
        ttk.Label(results_frame, textvariable=self.expected_var, font=("Courier", 10)).grid(row=0, column=1, sticky="w", pady=3)

        # Actual Result
        ttk.Label(results_frame, text="Actual (Computed) Result:").grid(row=1, column=0, sticky="w", pady=3)
        ttk.Label(results_frame, textvariable=self.actual_var, font=("Courier", 10)).grid(row=1, column=1, sticky="w", pady=3)

        # Absolute Error
        ttk.Label(results_frame, text="Absolute Error:", foreground="red").grid(row=2, column=0, sticky="w", pady=3)
        ttk.Label(results_frame, textvariable=self.abs_error_var, font=("Courier", 10), foreground="red").grid(row=2, column=1, sticky="w", pady=3)

        # Relative Error
        ttk.Label(results_frame, text="Relative Error (%):", foreground="red").grid(row=3, column=0, sticky="w", pady=3)
        ttk.Label(results_frame, textvariable=self.rel_error_var, font=("Courier", 10), foreground="red").grid(row=3, column=1, sticky="w", pady=3)

    def _create_plot(self, parent):
        """Creates the Matplotlib canvas for plotting the error."""
        plot_frame = ttk.LabelFrame(parent, text="Error Accumulation Graph", padding="10")
        plot_frame.grid(row=5, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        plot_frame.rowconfigure(0, weight=1)
        plot_frame.columnconfigure(0, weight=1)

        fig = Figure(figsize=(7, 4), dpi=100)
        self.ax = fig.add_subplot(111)
        
        self.canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.canvas.draw()
        
    def run_analysis(self):
        """Performs the calculation and updates the GUI."""
        try:
            large_num_str = self.large_num_var.get()
            small_num_str = self.small_num_var.get()
            iterations = int(self.iterations_var.get())
            
            # Use Decimal for high-precision ground truth
            large_num_dec = Decimal(large_num_str)
            small_num_dec = Decimal(small_num_str)
            
            # Select the floating point precision for the simulation
            if self.precision_var.get() == "Single (32-bit)":
                dtype = np.float32
            else:
                dtype = np.float64
                
            # Convert inputs to the chosen numpy float type
            large_num_float = dtype(large_num_str)
            small_num_float = dtype(small_num_str)

        except (ValueError, TypeError):
            messagebox.showerror("Invalid Input", "Please enter valid numbers.")
            return

        # 1. Calculate the "actual" result using an iterative loop (this is where errors accumulate)
        actual_result = large_num_float
        errors_over_time = []
        iteration_steps = range(1, iterations + 1)
        
        for i in iteration_steps:
            actual_result += small_num_float
            # Calculate the error at this step for plotting
            current_expected_dec = large_num_dec + (Decimal(i) * small_num_dec)
            current_error = abs(Decimal(str(actual_result)) - current_expected_dec)
            errors_over_time.append(current_error)

        # 2. Calculate the "expected" result using high-precision Decimal
        expected_result_dec = large_num_dec + (Decimal(iterations) * small_num_dec)

        # 3. Calculate final errors
        absolute_error = abs(Decimal(str(actual_result)) - expected_result_dec)
        
        if expected_result_dec != 0:
            relative_error_percent = (absolute_error / abs(expected_result_dec)) * 100
        else:
            relative_error_percent = Decimal(0)

        # 4. Update the result labels
        self.expected_var.set(f"{expected_result_dec:,.15f}")
        self.actual_var.set(f"{actual_result:,.15f}")
        self.abs_error_var.set(f"{absolute_error:.15e}") # Scientific notation for error
        self.rel_error_var.set(f"{relative_error_percent:.15f} %")
        
        # 5. Update the plot
        self.ax.clear()
        self.ax.plot(iteration_steps, errors_over_time)
        self.ax.set_title(f"Accumulated Absolute Error ({dtype.__name__})")
        self.ax.set_xlabel("Number of Additions")
        self.ax.set_ylabel("Absolute Error")
        self.ax.grid(True)
        self.ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0)) # Scientific notation for y-axis
        self.canvas.draw()


if __name__ == "__main__":
    app = FloatingPointErrorAnalyzer()
    app.mainloop()
    