/**
 * Legislative Complexity Meter
 * 
 * An interactive component that visualizes the complexity of legislative bills
 * with animated effects and hover interactions.
 */

class ComplexityMeter {
  constructor(elementId, options = {}) {
    // Get the container element
    this.container = document.getElementById(elementId);
    if (!this.container) {
      console.error(`Element with ID "${elementId}" not found.`);
      return;
    }
    
    // Default options
    this.options = {
      minValue: 0,
      maxValue: 100,
      thresholds: [30, 70],
      colors: ['#28a745', '#ffc107', '#dc3545'],
      animationDuration: 1000,
      showLabels: true,
      tooltipEnabled: true,
      tooltipFormat: (value) => `Complexity: ${value}%`,
      labelFormat: (value) => `${value}%`,
      ...options
    };
    
    // Initialize state
    this.value = this.options.minValue;
    this.previousValue = this.options.minValue;
    this.animationStart = null;
    this.animating = false;
    
    // Create meter components
    this.createMeterElements();
    
    // Initial render
    this.render();
  }
  
  createMeterElements() {
    // Clear container
    this.container.innerHTML = '';
    this.container.classList.add('complexity-meter-container');
    
    // Create meter wrapper
    this.wrapper = document.createElement('div');
    this.wrapper.className = 'complexity-meter-wrapper';
    this.container.appendChild(this.wrapper);
    
    // Create meter background
    this.background = document.createElement('div');
    this.background.className = 'complexity-meter-background';
    this.wrapper.appendChild(this.background);
    
    // Create meter fill
    this.fill = document.createElement('div');
    this.fill.className = 'complexity-meter-fill';
    this.wrapper.appendChild(this.fill);
    
    // Create meter marker
    this.marker = document.createElement('div');
    this.marker.className = 'complexity-meter-marker';
    this.wrapper.appendChild(this.marker);
    
    // Create threshold markers
    this.thresholdMarkers = [];
    this.options.thresholds.forEach((threshold, index) => {
      const marker = document.createElement('div');
      marker.className = 'complexity-meter-threshold';
      marker.style.left = `${threshold}%`;
      marker.setAttribute('data-threshold', threshold);
      this.wrapper.appendChild(marker);
      this.thresholdMarkers.push(marker);
    });
    
    // Create labels if enabled
    if (this.options.showLabels) {
      this.valueLabel = document.createElement('div');
      this.valueLabel.className = 'complexity-meter-label';
      this.container.appendChild(this.valueLabel);
    }
    
    // Create tooltip if enabled
    if (this.options.tooltipEnabled) {
      this.tooltip = document.createElement('div');
      this.tooltip.className = 'complexity-meter-tooltip';
      this.tooltip.style.display = 'none';
      this.container.appendChild(this.tooltip);
      
      // Add event listeners for tooltip
      this.wrapper.addEventListener('mouseenter', this.showTooltip.bind(this));
      this.wrapper.addEventListener('mousemove', this.moveTooltip.bind(this));
      this.wrapper.addEventListener('mouseleave', this.hideTooltip.bind(this));
    }
  }
  
  setValue(value) {
    // Store previous value for animation
    this.previousValue = this.value;
    
    // Clamp value to min/max range
    this.value = Math.max(
      this.options.minValue,
      Math.min(this.options.maxValue, value)
    );
    
    // Begin animation
    this.startAnimation();
  }
  
  startAnimation() {
    // Skip animation if already animating
    if (this.animating) {
      this.render();
      return;
    }
    
    this.animating = true;
    this.animationStart = null;
    
    // Request animation frame
    requestAnimationFrame(this.animate.bind(this));
  }
  
  animate(timestamp) {
    if (!this.animationStart) {
      this.animationStart = timestamp;
    }
    
    // Calculate progress of animation (0 to 1)
    const elapsed = timestamp - this.animationStart;
    const progress = Math.min(elapsed / this.options.animationDuration, 1);
    
    // Calculate current animated value
    const animatedValue = this.previousValue + (this.value - this.previousValue) * this.easeOutQuad(progress);
    
    // Update the meter display
    this.updateMeter(animatedValue);
    
    // Continue animation if not complete
    if (progress < 1) {
      requestAnimationFrame(this.animate.bind(this));
    } else {
      this.animating = false;
    }
  }
  
  easeOutQuad(t) {
    return t * (2 - t);
  }
  
  updateMeter(value) {
    // Calculate percentage for styles
    const percentage = ((value - this.options.minValue) / 
                        (this.options.maxValue - this.options.minValue)) * 100;
    
    // Update fill width
    this.fill.style.width = `${percentage}%`;
    
    // Update marker position
    this.marker.style.left = `${percentage}%`;
    
    // Update color based on thresholds
    const color = this.getColorForValue(percentage);
    this.fill.style.backgroundColor = color;
    this.marker.style.backgroundColor = color;
    
    // Update value label if enabled
    if (this.options.showLabels && this.valueLabel) {
      this.valueLabel.textContent = this.options.labelFormat(Math.round(value));
      
      // Position label strategically
      if (percentage < 20) {
        this.valueLabel.style.left = `${percentage + 5}%`;
        this.valueLabel.style.transform = 'translateX(0)';
      } else if (percentage > 80) {
        this.valueLabel.style.right = `${100 - percentage + 5}%`;
        this.valueLabel.style.left = 'auto';
        this.valueLabel.style.transform = 'translateX(0)';
      } else {
        this.valueLabel.style.left = `${percentage}%`;
        this.valueLabel.style.right = 'auto';
        this.valueLabel.style.transform = 'translateX(-50%)';
      }
    }
  }
  
  getColorForValue(percentage) {
    // Default to first color if below first threshold
    if (percentage <= this.options.thresholds[0]) {
      return this.options.colors[0];
    }
    
    // Use last color if above last threshold
    if (percentage >= this.options.thresholds[this.options.thresholds.length - 1]) {
      return this.options.colors[this.options.colors.length - 1];
    }
    
    // Find appropriate color based on thresholds
    for (let i = 0; i < this.options.thresholds.length - 1; i++) {
      if (percentage >= this.options.thresholds[i] && 
          percentage < this.options.thresholds[i + 1]) {
        return this.options.colors[i + 1];
      }
    }
    
    // Default fallback
    return this.options.colors[0];
  }
  
  showTooltip(event) {
    if (this.tooltip) {
      this.tooltip.style.display = 'block';
      this.moveTooltip(event);
    }
  }
  
  moveTooltip(event) {
    if (!this.tooltip) return;
    
    // Calculate relative position within meter
    const rect = this.wrapper.getBoundingClientRect();
    const relativeX = Math.max(0, Math.min(1, (event.clientX - rect.left) / rect.width));
    
    // Calculate value at cursor position
    const value = this.options.minValue + 
                 (this.options.maxValue - this.options.minValue) * relativeX;
    
    // Update tooltip content
    this.tooltip.textContent = this.options.tooltipFormat(Math.round(value));
    
    // Position tooltip above cursor
    this.tooltip.style.left = `${event.clientX - rect.left}px`;
    this.tooltip.style.top = `${event.clientY - rect.top - 30}px`;
    this.tooltip.style.transform = 'translateX(-50%)';
  }
  
  hideTooltip() {
    if (this.tooltip) {
      this.tooltip.style.display = 'none';
    }
  }
  
  render() {
    this.updateMeter(this.value);
  }
}

// Create a function to measure legislative complexity
function calculateLegislativeComplexity(bill) {
  if (!bill) return 0;
  
  let complexity = 0;
  
  // Factors that increase complexity
  const factors = {
    lengthFactor: 0.1,        // Longer descriptions are more complex
    wordCountFactor: 0.2,     // More words in the title indicate complexity
    statusFactor: {           // Different statuses have different complexities
      'Pending': 20,
      'Active': 40,
      'Passed': 70,
      'Failed': 30
    },
    ageInDaysFactor: 0.05     // Older bills tend to be more complex
  };
  
  // Calculate complexity based on description length
  if (bill.description) {
    complexity += Math.min(50, bill.description.length * factors.lengthFactor);
  }
  
  // Calculate complexity based on title word count
  if (bill.title) {
    const wordCount = bill.title.split(' ').length;
    complexity += Math.min(25, wordCount * factors.wordCountFactor);
  }
  
  // Add complexity based on status
  if (bill.status && factors.statusFactor[bill.status]) {
    complexity += factors.statusFactor[bill.status];
  }
  
  // Add complexity based on age
  if (bill.last_action_date) {
    const lastActionDate = new Date(bill.last_action_date);
    const currentDate = new Date();
    const ageInDays = Math.floor((currentDate - lastActionDate) / (1000 * 60 * 60 * 24));
    complexity += Math.min(15, ageInDays * factors.ageInDaysFactor);
  }
  
  // Ensure complexity is within 0-100 range
  return Math.max(0, Math.min(100, Math.round(complexity)));
}

// Attach to window object for global access
window.ComplexityMeter = ComplexityMeter;
window.calculateLegislativeComplexity = calculateLegislativeComplexity;