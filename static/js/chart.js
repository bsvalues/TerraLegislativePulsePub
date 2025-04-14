/**
 * Benton County Assessor AI Platform - Chart Utilities
 * Provides functions for creating and updating charts throughout the application
 */

/**
 * Create a property value comparison chart
 * @param {string} canvasId - The ID of the canvas element
 * @param {object} valuationData - The valuation data to display
 */
function createValueComparisonChart(canvasId, valuationData) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    
    // Extract values based on the valuation approach
    let values = [];
    let labels = [];
    let colors = [];
    
    // Determine which data to show based on what's available
    if (valuationData.market_value) {
        labels.push('Market Value');
        values.push(valuationData.market_value);
        colors.push('rgba(54, 162, 235, 0.7)');
    } else if (valuationData.cost_value) {
        labels.push('Replacement Cost');
        values.push(valuationData.replacement_cost);
        colors.push('rgba(255, 159, 64, 0.7)');
        
        labels.push('Depreciated Cost');
        values.push(valuationData.depreciated_cost);
        colors.push('rgba(255, 99, 132, 0.7)');
        
        labels.push('Land Value');
        values.push(valuationData.land_value);
        colors.push('rgba(75, 192, 192, 0.7)');
        
        labels.push('Total Value');
        values.push(valuationData.cost_value);
        colors.push('rgba(153, 102, 255, 0.7)');
    } else if (valuationData.income_value) {
        labels.push('Potential Gross Income');
        values.push(valuationData.potential_gross_income);
        colors.push('rgba(255, 159, 64, 0.7)');
        
        labels.push('Effective Gross Income');
        values.push(valuationData.effective_gross_income);
        colors.push('rgba(75, 192, 192, 0.7)');
        
        labels.push('Net Operating Income');
        values.push(valuationData.net_operating_income);
        colors.push('rgba(54, 162, 235, 0.7)');
        
        labels.push('Income Value');
        values.push(valuationData.income_value);
        colors.push('rgba(153, 102, 255, 0.7)');
    }
    
    // Create the chart
    new Chart(canvas, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Property Value Components',
                data: values,
                backgroundColor: colors,
                borderColor: colors.map(color => color.replace('0.7', '1')),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return formatCurrency(context.raw);
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return formatCurrency(value);
                        }
                    }
                }
            }
        }
    });
}

/**
 * Create a legislative impact chart
 * @param {string} canvasId - The ID of the canvas element
 * @param {object} impactData - The impact data to display
 */
function createLegislativeImpactChart(canvasId, impactData) {
    const canvas = document.getElementById(canvasId);
    if (!canvas || !impactData || !impactData.property_class_impact) return;
    
    const propertyClasses = Object.keys(impactData.property_class_impact);
    const impactLevels = propertyClasses.map(pc => {
        const impact = impactData.property_class_impact[pc].impact;
        // Convert impact levels to numeric values for the chart
        switch(impact) {
            case 'high': return 3;
            case 'medium': return 2;
            case 'low': return 1;
            default: return 0;
        }
    });
    
    // Create color array based on impact
    const colors = impactLevels.map(level => {
        switch(level) {
            case 3: return 'rgba(255, 99, 132, 0.7)'; // high - red
            case 2: return 'rgba(255, 159, 64, 0.7)'; // medium - orange
            case 1: return 'rgba(75, 192, 192, 0.7)'; // low - teal
            default: return 'rgba(201, 203, 207, 0.7)'; // none - gray
        }
    });
    
    // Create the chart
    new Chart(canvas, {
        type: 'bar',
        data: {
            labels: propertyClasses,
            datasets: [{
                label: 'Impact Level',
                data: impactLevels,
                backgroundColor: colors,
                borderColor: colors.map(color => color.replace('0.7', '1')),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const level = context.raw;
                            switch(level) {
                                case 3: return 'High Impact';
                                case 2: return 'Medium Impact';
                                case 1: return 'Low Impact';
                                default: return 'No Impact';
                            }
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 3,
                    ticks: {
                        stepSize: 1,
                        callback: function(value) {
                            switch(value) {
                                case 3: return 'High';
                                case 2: return 'Medium';
                                case 1: return 'Low';
                                case 0: return 'None';
                                default: return '';
                            }
                        }
                    }
                }
            }
        }
    });
}

/**
 * Create a dashboard summary chart
 * @param {string} canvasId - The ID of the canvas element
 * @param {object} data - The data to display
 */
function createDashboardSummaryChart(canvasId, data) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    
    // Sample data structure
    // data = {
    //   labels: ['Residential', 'Commercial', 'Industrial', 'Agricultural', 'Vacant Land', 'Public'],
    //   values: [245, 78, 34, 57, 89, 12]
    // }
    
    // Create the chart
    new Chart(canvas, {
        type: 'doughnut',
        data: {
            labels: data.labels,
            datasets: [{
                data: data.values,
                backgroundColor: [
                    'rgba(54, 162, 235, 0.7)',
                    'rgba(255, 99, 132, 0.7)',
                    'rgba(255, 159, 64, 0.7)',
                    'rgba(75, 192, 192, 0.7)',
                    'rgba(153, 102, 255, 0.7)',
                    'rgba(201, 203, 207, 0.7)'
                ],
                borderColor: [
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 99, 132, 1)',
                    'rgba(255, 159, 64, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(153, 102, 255, 1)',
                    'rgba(201, 203, 207, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right'
                }
            }
        }
    });
}

/**
 * Create a property assessment trend chart
 * @param {string} canvasId - The ID of the canvas element
 * @param {object} data - The data to display
 */
function createAssessmentTrendChart(canvasId, data) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    
    // Sample data structure
    // data = {
    //   labels: ['2020', '2021', '2022', '2023', '2024', '2025'],
    //   values: [220000, 235000, 245000, 260000, 275000, 290000]
    // }
    
    // Create the chart
    new Chart(canvas, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Assessed Value',
                data: data.values,
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 2,
                fill: true,
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return formatCurrency(context.raw);
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    ticks: {
                        callback: function(value) {
                            return formatCurrency(value);
                        }
                    }
                }
            }
        }
    });
}
