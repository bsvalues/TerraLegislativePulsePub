/**
 * Benton County Assessor AI Platform - Main JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    
    // Initialize popovers
    const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
    const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl));
    
    // Add event listeners for dynamic elements
    setupFormValidation();
    setupToggleButtons();
    setupAnalysisTypeSelection();
    setupPropertyClassSelector();
});

/**
 * Set up form validation for all forms
 */
function setupFormValidation() {
    // Get all forms with the 'needs-validation' class
    const forms = document.querySelectorAll('.needs-validation');
    
    // Loop over each form and prevent submission if validation fails
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        }, false);
    });
}

/**
 * Set up toggle buttons (e.g., for showing/hiding sections)
 */
function setupToggleButtons() {
    const toggleButtons = document.querySelectorAll('[data-toggle-target]');
    
    toggleButtons.forEach(button => {
        button.addEventListener('click', () => {
            const targetId = button.getAttribute('data-toggle-target');
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                // Toggle the 'd-none' class to show/hide the element
                targetElement.classList.toggle('d-none');
                
                // Update button text if data attributes are provided
                const showText = button.getAttribute('data-show-text');
                const hideText = button.getAttribute('data-hide-text');
                
                if (showText && hideText) {
                    button.textContent = targetElement.classList.contains('d-none') ? showText : hideText;
                }
            }
        });
    });
}

/**
 * Set up the analysis type selection in the legislative impact page
 */
function setupAnalysisTypeSelection() {
    const analysisTypeRadios = document.querySelectorAll('input[name="analysis_type"]');
    const billSection = document.getElementById('bill-analysis-section');
    const classSection = document.getElementById('class-analysis-section');
    const overviewSection = document.getElementById('overview-analysis-section');
    
    if (analysisTypeRadios.length && billSection && classSection && overviewSection) {
        analysisTypeRadios.forEach(radio => {
            radio.addEventListener('change', () => {
                // Hide all sections first
                billSection.classList.add('d-none');
                classSection.classList.add('d-none');
                overviewSection.classList.add('d-none');
                
                // Show the selected section
                if (radio.value === 'bill' && radio.checked) {
                    billSection.classList.remove('d-none');
                } else if (radio.value === 'property_class' && radio.checked) {
                    classSection.classList.remove('d-none');
                } else if (radio.value === 'overview' && radio.checked) {
                    overviewSection.classList.remove('d-none');
                }
            });
        });
    }
}

/**
 * Set up the property class selector to show applicable class codes
 */
function setupPropertyClassSelector() {
    const classSelector = document.getElementById('property_class');
    const codeDisplay = document.getElementById('class_codes_display');
    
    if (classSelector && codeDisplay) {
        // Define property classification codes as per WA state standards
        const propertyCodes = {
            'Residential': ['R1 - Single Family', 'R2 - Multi-Family', 'R3 - Condominiums', 'R4 - Mobile Homes'],
            'Commercial': ['C1 - Retail', 'C2 - Office', 'C3 - Mixed Use'],
            'Industrial': ['I1 - Light Industrial', 'I2 - Heavy Industrial', 'I3 - Warehouse'],
            'Agricultural': ['A1 - Cropland', 'A2 - Pasture'],
            'Vacant Land': ['V1 - Residential', 'V2 - Commercial'],
            'Public': ['P1 - Government', 'P2 - Non-Profit']
        };
        
        // Update the code display when the class selector changes
        classSelector.addEventListener('change', () => {
            const selectedClass = classSelector.value;
            const codes = propertyCodes[selectedClass] || [];
            
            if (codes.length > 0) {
                codeDisplay.innerHTML = '<small>Applicable codes: ' + codes.join(', ') + '</small>';
                codeDisplay.classList.remove('d-none');
            } else {
                codeDisplay.classList.add('d-none');
            }
        });
        
        // Initial update
        if (classSelector.value) {
            const event = new Event('change');
            classSelector.dispatchEvent(event);
        }
    }
}

/**
 * Format a number as currency
 */
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

/**
 * Format a date string
 */
function formatDate(dateString) {
    if (!dateString) return '';
    
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    }).format(date);
}

/**
 * Submit an API request to the MCP
 */
function submitApiRequest(endpoint, data, successCallback, errorCallback) {
    fetch(endpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            successCallback(data);
        } else {
            errorCallback(data.error || 'Unknown error occurred');
        }
    })
    .catch(error => {
        errorCallback('Network error: ' + error.message);
    });
}
