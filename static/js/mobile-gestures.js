/**
 * TerraLegislativePulse - Mobile Gesture Controls
 * 
 * This script handles mobile-friendly gesture controls:
 * - Swipe actions on bill cards
 * - Pull-to-refresh on lists
 * - Touch-friendly navigation
 * - Mobile sidebar controls
 */

class MobileGestures {
  constructor() {
    // Initialization
    this.initSwipeActions();
    this.initPullToRefresh();
    this.initMobileSidebar();
    this.initTouchNavigation();
    this.initResponsiveTable();
  }

  /**
   * Initialize swipe actions on list items
   */
  initSwipeActions() {
    // Find all swipe containers
    const swipeContainers = document.querySelectorAll('.swipe-container');
    
    swipeContainers.forEach(container => {
      const swipeItem = container.querySelector('.swipe-item');
      const swipeActions = container.querySelector('.swipe-actions');
      
      if (!swipeItem || !swipeActions) return;
      
      // Get width of actions for limit
      const actionsWidth = swipeActions.offsetWidth;
      
      // Touch variables
      let startX = 0;
      let currentX = 0;
      let isDragging = false;
      
      // Event handlers
      swipeItem.addEventListener('touchstart', e => {
        startX = e.touches[0].clientX;
        isDragging = true;
        swipeItem.style.transition = '';
      });
      
      swipeItem.addEventListener('touchmove', e => {
        if (!isDragging) return;
        
        currentX = e.touches[0].clientX;
        const diffX = currentX - startX;
        
        // Only allow swiping left
        if (diffX <= 0) {
          const translateX = Math.max(diffX, -actionsWidth);
          swipeItem.style.transform = `translateX(${translateX}px)`;
        }
      });
      
      const finishSwipe = e => {
        if (!isDragging) return;
        
        isDragging = false;
        swipeItem.style.transition = 'transform 0.3s ease';
        
        const diffX = currentX - startX;
        
        // If swiped more than half of the actions width, show actions
        if (diffX < -actionsWidth / 2) {
          swipeItem.style.transform = `translateX(-${actionsWidth}px)`;
        } else {
          swipeItem.style.transform = '';
        }
      };
      
      swipeItem.addEventListener('touchend', finishSwipe);
      swipeItem.addEventListener('touchcancel', finishSwipe);
      
      // Close swipe item on document touch
      document.addEventListener('touchstart', e => {
        const isInsideContainer = container.contains(e.target);
        
        if (!isInsideContainer) {
          swipeItem.style.transition = 'transform 0.3s ease';
          swipeItem.style.transform = '';
        }
      });
    });
  }

  /**
   * Initialize pull-to-refresh functionality
   */
  initPullToRefresh() {
    const pullContainers = document.querySelectorAll('.pull-container');
    
    pullContainers.forEach(container => {
      const content = container.querySelector('.pull-content');
      const indicator = container.querySelector('.pull-to-refresh');
      
      if (!content || !indicator) return;
      
      let startY = 0;
      let currentY = 0;
      let isDragging = false;
      let isRefreshing = false;
      
      // Touch threshold in pixels
      const threshold = 80;
      
      content.addEventListener('touchstart', e => {
        // Only allow pull when at the top of the content
        if (content.scrollTop > 0) return;
        
        startY = e.touches[0].clientY;
        isDragging = true;
      });
      
      content.addEventListener('touchmove', e => {
        if (!isDragging || isRefreshing) return;
        
        currentY = e.touches[0].clientY;
        const diffY = currentY - startY;
        
        // Only allow pulling down
        if (diffY > 0) {
          // Resistance effect - make it harder to pull as it gets further
          const resistance = 0.4;
          const pull = Math.min(diffY * resistance, threshold);
          
          content.style.transform = `translateY(${pull}px)`;
          
          // Show the indicator based on how far pulled
          indicator.style.transform = `translateY(${pull - threshold}px)`;
          
          // Visual feedback based on pull distance
          if (pull >= threshold) {
            indicator.querySelector('.pull-text').textContent = 'Release to refresh';
          } else {
            indicator.querySelector('.pull-text').textContent = 'Pull to refresh';
          }
          
          e.preventDefault();
        }
      });
      
      const finishPull = () => {
        if (!isDragging) return;
        
        isDragging = false;
        
        const diffY = currentY - startY;
        const pull = Math.min(diffY * 0.4, threshold);
        
        // If pulled past threshold, trigger refresh
        if (pull >= threshold) {
          isRefreshing = true;
          
          // Show refreshing indicator
          content.style.transition = 'transform 0.3s ease';
          content.style.transform = `translateY(50px)`;
          indicator.style.transition = 'transform 0.3s ease';
          indicator.style.transform = 'translateY(-30px)';
          indicator.querySelector('.pull-text').textContent = 'Refreshing...';
          indicator.querySelector('.spinner').style.display = 'inline-block';
          
          // Simulate refresh (replace with actual refresh)
          setTimeout(() => {
            // Reset positions
            content.style.transition = 'transform 0.3s ease';
            content.style.transform = '';
            indicator.style.transition = 'transform 0.3s ease';
            indicator.style.transform = 'translateY(-100%)';
            
            // Reset state after animation completes
            setTimeout(() => {
              isRefreshing = false;
              indicator.querySelector('.spinner').style.display = 'none';
              
              // Trigger page refresh
              window.location.reload();
            }, 300);
          }, 1500);
        } else {
          // Reset positions if not pulled enough
          content.style.transition = 'transform 0.3s ease';
          content.style.transform = '';
          indicator.style.transition = 'transform 0.3s ease';
          indicator.style.transform = 'translateY(-100%)';
        }
      };
      
      content.addEventListener('touchend', finishPull);
      content.addEventListener('touchcancel', finishPull);
    });
  }

  /**
   * Initialize mobile sidebar navigation
   */
  initMobileSidebar() {
    const toggleButton = document.querySelector('.navbar-toggler');
    const sidebar = document.querySelector('.sidebar');
    
    if (!toggleButton || !sidebar) return;
    
    // Create mobile sidebar and backdrop if they don't exist
    let mobileSidebar = document.querySelector('.mobile-sidebar');
    let backdrop = document.querySelector('.mobile-sidebar-backdrop');
    
    if (!mobileSidebar) {
      mobileSidebar = document.createElement('div');
      mobileSidebar.className = 'mobile-sidebar d-lg-none';
      mobileSidebar.innerHTML = sidebar.innerHTML;
      document.body.appendChild(mobileSidebar);
    }
    
    if (!backdrop) {
      backdrop = document.createElement('div');
      backdrop.className = 'mobile-sidebar-backdrop d-lg-none';
      document.body.appendChild(backdrop);
    }
    
    // Toggle sidebar on button click
    toggleButton.addEventListener('click', e => {
      e.preventDefault();
      mobileSidebar.classList.toggle('show');
      backdrop.classList.toggle('show');
      document.body.classList.toggle('sidebar-open');
    });
    
    // Close sidebar on backdrop click
    backdrop.addEventListener('click', () => {
      mobileSidebar.classList.remove('show');
      backdrop.classList.remove('show');
      document.body.classList.remove('sidebar-open');
    });
    
    // Handle swipe to open/close sidebar
    let startX = 0;
    let currentX = 0;
    
    document.addEventListener('touchstart', e => {
      startX = e.touches[0].clientX;
    });
    
    document.addEventListener('touchmove', e => {
      currentX = e.touches[0].clientX;
      const diffX = currentX - startX;
      
      // Swipe right to open sidebar (only when near left edge)
      if (startX < 30 && diffX > 50 && !mobileSidebar.classList.contains('show')) {
        mobileSidebar.classList.add('show');
        backdrop.classList.add('show');
        document.body.classList.add('sidebar-open');
      }
      
      // Swipe left to close sidebar
      if (diffX < -50 && mobileSidebar.classList.contains('show')) {
        mobileSidebar.classList.remove('show');
        backdrop.classList.remove('show');
        document.body.classList.remove('sidebar-open');
      }
    });
  }

  /**
   * Initialize touch-friendly navigation controls
   */
  initTouchNavigation() {
    // Make tabs larger and more touch-friendly
    const tabLinks = document.querySelectorAll('.nav-tabs .nav-link');
    tabLinks.forEach(tab => {
      tab.addEventListener('touchstart', () => {
        tab.classList.add('touch-active');
      });
      
      tab.addEventListener('touchend', () => {
        setTimeout(() => {
          tab.classList.remove('touch-active');
        }, 150);
      });
    });
    
    // Add mobile action menu button
    const actionContainer = document.querySelector('.bill-actions');
    
    if (window.innerWidth <= 768 && actionContainer && !document.querySelector('.mobile-menu-badge')) {
      const menuBadge = document.createElement('div');
      menuBadge.className = 'mobile-menu-badge d-lg-none';
      menuBadge.innerHTML = '<i class="bi bi-three-dots-vertical"></i>';
      document.body.appendChild(menuBadge);
      
      menuBadge.addEventListener('click', () => {
        // Show actions in a modal
        const actionsModal = new bootstrap.Modal(document.getElementById('mobileActionsModal'));
        actionsModal.show();
      });
    }
  }

  /**
   * Initialize responsive tables for mobile
   */
  initResponsiveTable() {
    // Only apply on small screens
    if (window.innerWidth <= 768) {
      const tables = document.querySelectorAll('table.table');
      
      tables.forEach(table => {
        // Create mobile view if it doesn't already exist
        if (!table.classList.contains('mobile-converted')) {
          const tableContainer = table.closest('.table-responsive');
          if (!tableContainer) return;
          
          const mobileView = document.createElement('div');
          mobileView.className = 'mobile-table-view d-md-none';
          
          // Get headers
          const headers = Array.from(table.querySelectorAll('thead th')).map(th => th.textContent.trim());
          
          // Convert each row to a card
          const rows = table.querySelectorAll('tbody tr');
          
          rows.forEach(row => {
            // Create card
            const card = document.createElement('div');
            card.className = 'mobile-table-card card border-0 shadow-sm';
            
            // Get title from first column
            const titleCol = row.querySelector('td');
            if (!titleCol) return;
            
            // Create card header
            const cardHeader = document.createElement('div');
            cardHeader.className = 'mobile-table-card-header';
            cardHeader.textContent = titleCol.textContent.trim();
            card.appendChild(cardHeader);
            
            // Create card body
            const cardBody = document.createElement('div');
            cardBody.className = 'mobile-table-card-body';
            
            // Add each cell as an item
            const cells = row.querySelectorAll('td');
            
            cells.forEach((cell, index) => {
              // Skip first column as it's the header
              if (index === 0) return;
              
              // Skip if there's no corresponding header
              if (!headers[index]) return;
              
              const item = document.createElement('div');
              item.className = 'mobile-table-card-item';
              
              const label = document.createElement('div');
              label.className = 'mobile-table-card-label';
              label.textContent = headers[index];
              
              const value = document.createElement('div');
              value.className = 'mobile-table-card-value';
              value.innerHTML = cell.innerHTML;
              
              item.appendChild(label);
              item.appendChild(value);
              cardBody.appendChild(item);
            });
            
            // Add actions from last column
            const actions = row.querySelector('td:last-child');
            if (actions && actions.querySelector('.btn-group')) {
              const actionsItem = document.createElement('div');
              actionsItem.className = 'mobile-table-card-actions mt-3 pt-2 border-top';
              actionsItem.innerHTML = actions.innerHTML;
              cardBody.appendChild(actionsItem);
            }
            
            card.appendChild(cardBody);
            mobileView.appendChild(card);
          });
          
          // Add mobile view to DOM
          tableContainer.parentNode.insertBefore(mobileView, tableContainer);
          
          // Hide table on mobile, show on larger screens
          tableContainer.classList.add('d-none', 'd-md-block');
          
          // Mark table as converted
          table.classList.add('mobile-converted');
        }
      });
    }
  }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  const mobileGestures = new MobileGestures();
  
  // Handle resize events to reinitialize mobile-specific features
  window.addEventListener('resize', () => {
    if (window.innerWidth <= 768) {
      mobileGestures.initResponsiveTable();
    }
  });
});