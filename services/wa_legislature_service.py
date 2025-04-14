import requests
import logging
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

def get_wa_legislature_data(bill_id):
    """
    Get information about a bill from the Washington State Legislature website
    
    Args:
        bill_id (str): The bill ID to look up
        
    Returns:
        dict: Bill data from the WA Legislature website, or None if an error occurs
    """
    try:
        # Parse the bill ID to extract components
        # Format is typically like "HB 1234" or "SB 5678"
        bill_parts = bill_id.split()
        if len(bill_parts) != 2:
            logger.error(f"Invalid bill ID format: {bill_id}")
            return None
        
        bill_type = bill_parts[0].lower()  # e.g., "hb" or "sb"
        bill_number = bill_parts[1]  # e.g., "1234"
        
        # Construct the WA Legislature website URL
        session_year = "2025-26"  # Current biennium
        url = f"https://app.leg.wa.gov/billsummary?BillNumber={bill_number}&Year={session_year}&Initiative=false&BillId={bill_type}%20{bill_number}"
        
        # Make the HTTP request
        response = requests.get(url)
        
        # Check for successful response
        if response.status_code == 200:
            # Parse the HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract bill information
            title_element = soup.find('span', {'id': 'billTitle'})
            title = title_element.text.strip() if title_element else "Title not found"
            
            sponsor_element = soup.find('span', {'id': 'billSponsors'})
            sponsors = sponsor_element.text.strip() if sponsor_element else "Sponsors not found"
            
            description_element = soup.find('div', {'class': 'bill-description'})
            description = description_element.text.strip() if description_element else "Description not found"
            
            status_element = soup.find('div', {'class': 'bill-status'})
            status = status_element.text.strip() if status_element else "Status not found"
            
            # Extract bill history
            history_table = soup.find('table', {'class': 'bill-history'})
            history = []
            if history_table:
                rows = history_table.find_all('tr')
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 2:
                        date = cells[0].text.strip()
                        action = cells[1].text.strip()
                        history.append({
                            'date': date,
                            'action': action
                        })
            
            # Return the structured bill data
            return {
                'bill_id': bill_id,
                'title': title,
                'sponsors': sponsors,
                'description': description,
                'status': status,
                'history': history,
                'url': url
            }
        else:
            logger.error(f"WA Legislature website HTTP error: {response.status_code}")
            return None
        
    except Exception as e:
        logger.exception(f"Error retrieving bill data from WA Legislature website: {str(e)}")
        return None

def search_wa_bills(keyword):
    """
    Search for bills on the Washington State Legislature website
    
    Args:
        keyword (str): The keyword to search for
        
    Returns:
        list: List of bills matching the search, or empty list if an error occurs
    """
    try:
        # Construct the WA Legislature website search URL
        session_year = "2025-26"  # Current biennium
        url = f"https://app.leg.wa.gov/billsbytopic?Year={session_year}"
        
        # Make the HTTP request
        response = requests.get(url)
        
        # Check for successful response
        if response.status_code == 200:
            # Parse the HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all bill links
            bills = []
            bill_links = soup.select('a[href*="billsummary"]')
            
            for link in bill_links:
                bill_id = link.text.strip()
                bill_url = "https://app.leg.wa.gov" + link['href']
                
                # Check if the keyword is in the link text or parent element's text
                parent_text = link.parent.text.strip() if link.parent else ""
                
                if keyword.lower() in parent_text.lower():
                    # Get the bill description from the parent element
                    description = parent_text.replace(bill_id, "").strip()
                    
                    bills.append({
                        'bill_id': bill_id,
                        'description': description,
                        'url': bill_url
                    })
            
            return bills
        else:
            logger.error(f"WA Legislature website HTTP error: {response.status_code}")
            return []
        
    except Exception as e:
        logger.exception(f"Error searching bills on WA Legislature website: {str(e)}")
        return []

def get_recent_wa_bills(limit=10):
    """
    Get recent bills from the Washington State Legislature website
    
    Args:
        limit (int): The maximum number of bills to retrieve
        
    Returns:
        list: List of recent bills, or empty list if an error occurs
    """
    try:
        # Construct the WA Legislature website recent bills URL
        session_year = "2025-26"  # Current biennium
        url = f"https://app.leg.wa.gov/billinfo/prefiled.aspx?year={session_year}"
        
        # Make the HTTP request
        response = requests.get(url)
        
        # Check for successful response
        if response.status_code == 200:
            # Parse the HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all bill links
            bills = []
            bill_links = soup.select('a[href*="billsummary"]')
            
            for link in bill_links[:limit]:
                bill_id = link.text.strip()
                bill_url = "https://app.leg.wa.gov" + link['href']
                
                # Get the bill description from the parent element
                parent_text = link.parent.text.strip() if link.parent else ""
                description = parent_text.replace(bill_id, "").strip()
                
                bills.append({
                    'bill_id': bill_id,
                    'description': description,
                    'url': bill_url
                })
            
            return bills
        else:
            logger.error(f"WA Legislature website HTTP error: {response.status_code}")
            return []
        
    except Exception as e:
        logger.exception(f"Error retrieving recent bills from WA Legislature website: {str(e)}")
        return []
