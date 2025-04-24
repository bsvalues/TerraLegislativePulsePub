"""
Add Sample Bills

This script adds sample legislative bills to the database for testing purposes.
"""

import logging
from datetime import datetime, timedelta
from app import app, db
from models import LegislativeUpdate

logger = logging.getLogger(__name__)

def add_sample_bills():
    """Add sample bills to the database"""
    with app.app_context():
        # Check if bills already exist
        existing_count = LegislativeUpdate.query.count()
        if existing_count > 0:
            logger.info(f"{existing_count} bills already exist in the database")
            return
        
        # Sample bills from different sources
        sample_bills = [
            # WA Legislature bills
            {
                'bill_id': 'HB 1234',
                'title': 'Amending property tax assessment methods for agricultural land',
                'description': """
                NEW SECTION. Sec. 1. The legislature finds that:
                (1) Agriculture is a vital sector of the state's economy, providing jobs, economic activity, and essential food products.
                (2) Agricultural land valuation methods require updating to reflect modern farming practices and market conditions.
                (3) Current assessment methodologies may not adequately account for variations in soil quality, water rights, and other factors affecting agricultural land productivity.
                
                NEW SECTION. Sec. 2. RCW 84.34.065 is amended to read as follows:
                (1) The true and fair value of farm and agricultural land shall be determined by consideration of the earning or productive capacity of comparable lands from crops grown most typically in the area averaged over not less than five years.
                (2) County assessors shall establish a comprehensive soil classification system that accounts for:
                   (a) Soil type and quality;
                   (b) Water availability and rights;
                   (c) Topography and elevation;
                   (d) Climate zone characteristics; and
                   (e) Other factors affecting agricultural productivity.
                (3) Assessment values shall be adjusted annually based on a five-year rolling average of agricultural commodity prices as published by the state department of agriculture.
                """,
                'source': 'wa_legislature',
                'url': 'https://app.leg.wa.gov/billsummary?BillNumber=1234&Year=2023',
                'status': 'Active',
                'introduced_date': datetime.now() - timedelta(days=45),
                'last_action_date': datetime.now() - timedelta(days=15),
                'impact_summary': 'Changes agricultural property valuation methods to account for soil quality and water rights.',
                'affected_property_classes': 'Agricultural'
            },
            {
                'bill_id': 'SB 5678',
                'title': 'Revisions to commercial property valuation formulas',
                'description': """
                NEW SECTION. Sec. 1. The legislature recognizes that:
                (1) Commercial property valuation methodologies must adapt to changing market conditions and business practices.
                (2) The income approach to valuation requires standardization to ensure fairness and consistency across counties.
                
                NEW SECTION. Sec. 2. A new section is added to chapter 84.40 RCW to read as follows:
                (1) When valuing commercial properties using the income approach, county assessors shall:
                   (a) Utilize standardized capitalization rates based on property class, location, and quality;
                   (b) Consider vacancy rates within the relevant market area;
                   (c) Factor in actual operating expenses when available or standardized expense ratios when actual data is not available;
                   (d) Apply a standardized methodology for valuing properties with long-term leases; and
                   (e) Account for functional obsolescence in older commercial structures.
                (2) The department of revenue shall publish annual guidance on appropriate capitalization rates and expense ratios for different commercial property classes.
                (3) Implementation of this section shall be completed by January 1, 2026.
                """,
                'source': 'wa_legislature',
                'url': 'https://app.leg.wa.gov/billsummary?BillNumber=5678&Year=2023',
                'status': 'Active',
                'introduced_date': datetime.now() - timedelta(days=60),
                'last_action_date': datetime.now() - timedelta(days=10),
                'impact_summary': 'Standardizes commercial property valuation methodologies using the income approach.',
                'affected_property_classes': 'Commercial'
            },
            
            # OpenStates bills
            {
                'bill_id': 'HB 2468',
                'title': 'Expansion of residential property tax exemptions',
                'description': """
                AN ACT Relating to residential property tax relief; amending RCW 84.36.381; and creating new sections.
                
                NEW SECTION. Sec. 1. The legislature finds that:
                (1) Rising property taxes have placed a significant burden on senior citizens, disabled persons, and low-income homeowners.
                (2) Expanding property tax exemptions is necessary to help these vulnerable populations remain in their homes.
                
                Sec. 2. RCW 84.36.381 is amended to read as follows:
                (1) A person is exempt from any legal obligation to pay all or a portion of the amount of excess and regular real property taxes due and payable in the year following the year in which a claim is filed, and thereafter, in accordance with the following:
                   (a) The property taxes must have been imposed upon a residence which was occupied by the person claiming the exemption as a principal place of residence as of the time of filing;
                   (b) The person claiming the exemption must have owned the residence in fee, as a life estate, or by contract purchase at the time of filing;
                   (c) The person claiming the exemption must be:
                      (i) Sixty-five years of age or older on December 31st of the year in which the exemption claim is filed;
                      (ii) Retired from regular gainful employment by reason of disability; or
                      (iii) A veteran of the armed forces of the United States with a service-connected disability rating of eighty percent or higher;
                   (d) The combined disposable income of the person claiming the exemption and their spouse or domestic partner shall not exceed:
                      (i) Forty-five thousand dollars for the previous year; or
                      (ii) For applications filed on or after January 1, 2026, sixty thousand dollars for the previous year.
                """,
                'source': 'openstates',
                'url': 'https://openstates.org/wa/bills/2023-2024/HB2468/',
                'status': 'Active',
                'introduced_date': datetime.now() - timedelta(days=30),
                'last_action_date': datetime.now() - timedelta(days=5),
                'impact_summary': 'Expands property tax exemptions for seniors, disabled persons, and veterans.',
                'affected_property_classes': 'Residential'
            },
            {
                'bill_id': 'SB 3214',
                'title': 'Industrial property environmental impact assessment requirements',
                'description': """
                AN ACT Relating to environmental impact assessments for industrial properties; amending RCW 43.21C.030; and prescribing penalties.
                
                NEW SECTION. Sec. 1. The legislature finds that industrial properties may have significant environmental impacts that should be considered in property assessment and taxation.
                
                Sec. 2. RCW 43.21C.030 is amended to read as follows:
                (1) Industrial properties shall undergo an environmental impact assessment every five years to evaluate:
                   (a) Air quality impacts;
                   (b) Water quality impacts;
                   (c) Soil contamination;
                   (d) Hazardous materials management; and
                   (e) Potential remediation requirements.
                
                (2) County assessors shall incorporate environmental impact assessment results into industrial property valuations by:
                   (a) Adjusting for potential remediation costs;
                   (b) Accounting for environmental compliance investments; and
                   (c) Considering potential environmental liabilities in the property value determination.
                
                (3) The department of ecology shall establish standards for environmental impact assessments and provide technical assistance to county assessors.
                
                (4) Implementation of this section shall be completed by January 1, 2027.
                """,
                'source': 'openstates',
                'url': 'https://openstates.org/wa/bills/2023-2024/SB3214/',
                'status': 'Pending',
                'introduced_date': datetime.now() - timedelta(days=20),
                'last_action_date': datetime.now() - timedelta(days=3),
                'impact_summary': 'Requires environmental impact assessments for industrial properties and incorporates findings into valuations.',
                'affected_property_classes': 'Industrial'
            },
            
            # LegiScan bills
            {
                'bill_id': 'HB 3579',
                'title': 'Vacant land development incentives',
                'description': """
                AN ACT Relating to incentives for vacant land development; adding new sections to chapter 84.14 RCW; and creating new sections.
                
                NEW SECTION. Sec. 1. The legislature finds that:
                (1) Vacant land in urban areas represents an underutilized resource and opportunity for housing and economic development.
                (2) Tax incentives can effectively encourage the development of vacant land for productive uses.
                
                NEW SECTION. Sec. 2. A new section is added to chapter 84.14 RCW to read as follows:
                (1) Counties and cities may establish vacant land development zones where the following incentives apply:
                   (a) A three-year property tax exemption for development of vacant land for residential purposes;
                   (b) A five-year property tax exemption for development of vacant land for mixed-use purposes that include at least thirty percent affordable housing units; and
                   (c) Expedited permitting processes for qualifying development projects.
                
                (2) To qualify for incentives under this section, vacant land must:
                   (a) Have been undeveloped for at least five years;
                   (b) Be located within an urban growth area as defined in RCW 36.70A.110; and
                   (c) Not be subject to environmental remediation requirements.
                
                (3) Counties and cities establishing vacant land development zones shall:
                   (a) Create clear designation criteria;
                   (b) Establish monitoring and compliance mechanisms; and
                   (c) Report annually to the department of commerce on zone performance.
                
                (4) This section expires January 1, 2034.
                """,
                'source': 'legiscan',
                'url': 'https://legiscan.com/WA/bill/HB3579/2023',
                'status': 'Pending',
                'introduced_date': datetime.now() - timedelta(days=25),
                'last_action_date': datetime.now() - timedelta(days=8),
                'impact_summary': 'Creates tax incentives for vacant land development with special provisions for affordable housing.',
                'affected_property_classes': 'Vacant Land'
            },
            {
                'bill_id': 'SB 4102',
                'title': 'Public property assessment transparency',
                'description': """
                AN ACT Relating to public property assessment transparency; amending RCW 84.40.175; and creating new sections.
                
                NEW SECTION. Sec. 1. The legislature finds that:
                (1) Public properties that would be taxable if privately owned should be assessed for transparency purposes.
                (2) Assessments of public properties promote accountability and help citizens understand the value of public assets.
                
                Sec. 2. RCW 84.40.175 is amended to read as follows:
                (1) All property belonging exclusively to any federal, state, or local government shall be assessed and entered on the assessment roll with a detailed inventory.
                
                (2) County assessors shall:
                   (a) Assess public properties using the same methodologies applied to comparable private properties;
                   (b) Maintain a public database of all assessed government properties;
                   (c) Include assessed values of public properties in annual reports; and
                   (d) Update assessments of public properties at the same frequency as private properties.
                
                (3) The department of revenue shall establish standardized methodologies for assessing different classes of public properties.
                
                (4) Each government entity owning property shall designate a property coordinator to provide necessary information to county assessors.
                
                (5) Implementation of this section shall be completed by January 1, 2025.
                """,
                'source': 'legiscan',
                'url': 'https://legiscan.com/WA/bill/SB4102/2023',
                'status': 'Pending',
                'introduced_date': datetime.now() - timedelta(days=15),
                'last_action_date': datetime.now() - timedelta(days=2),
                'impact_summary': 'Requires assessment of public properties using methodologies consistent with private property assessments.',
                'affected_property_classes': 'Public'
            },
            
            # Local documents
            {
                'bill_id': 'WA-2025-014',
                'title': 'Washington County ordinance on property assessment appeals',
                'description': """
                WASHINGTON COUNTY ORDINANCE NO. WA-2025-014
                
                AN ORDINANCE relating to property assessment appeals; amending Washington County Code Chapter 4.40; and establishing effective dates.
                
                WHEREAS, the Washington County Board of Commissioners recognizes the importance of a fair and transparent property assessment appeals process; and
                
                WHEREAS, improvements to the appeals process can enhance taxpayer understanding and compliance; now, therefore,
                
                THE BOARD OF COUNTY COMMISSIONERS OF WASHINGTON COUNTY, WASHINGTON, DO ORDAIN AS FOLLOWS:
                
                Section 1. Washington County Code Chapter 4.40 is amended as follows:
                
                4.40.010 Assessment Appeal Process.
                (a) Property owners may appeal their property assessment by:
                    (1) Filing a petition with the Washington County Board of Equalization within thirty days of the date the assessment notice was mailed;
                    (2) Providing documentation supporting their appeal claim; and
                    (3) Participating in a pre-hearing conference with the County Assessor's office.
                
                (b) The County Assessor's office shall:
                    (1) Establish an online appeal filing system;
                    (2) Provide property owners with a detailed explanation of assessment methodologies;
                    (3) Offer pre-hearing conferences to potentially resolve disputes; and
                    (4) Maintain transparent records of all appeal outcomes.
                
                (c) The Board of Equalization shall:
                    (1) Schedule hearings within sixty days of petition filing;
                    (2) Provide appellants with at least fourteen days' notice of the hearing date;
                    (3) Make decisions based on evidence presented; and
                    (4) Issue written decisions within fourteen days of the hearing.
                
                Section 2. This ordinance shall take effect thirty days from the date of its passage.
                
                PASSED by the Board of County Commissioners of Washington County, Washington, at a regular meeting thereof, held this 15th day of March, 2025.
                """,
                'source': 'local_docs',
                'url': 'https://www.co.washington.wa.us/ordinances/WA-2025-014.pdf',
                'status': 'Passed',
                'introduced_date': datetime.now() - timedelta(days=40),
                'last_action_date': datetime.now() - timedelta(days=5),
                'impact_summary': 'Updates the property assessment appeals process to improve transparency and accessibility.',
                'affected_property_classes': 'Residential, Commercial, Industrial, Agricultural, Vacant Land, Public'
            },
            {
                'bill_id': 'WA-2025-021',
                'title': 'Washington County resolution on special assessment districts',
                'description': """
                WASHINGTON COUNTY RESOLUTION NO. WA-2025-021
                
                A RESOLUTION establishing guidelines for the creation and management of special assessment districts; and providing for implementation procedures.
                
                WHEREAS, special assessment districts provide a mechanism for funding specific improvements that benefit particular properties; and
                
                WHEREAS, standardized guidelines for special assessment districts will ensure equitable administration and transparent operations; now, therefore,
                
                BE IT RESOLVED BY THE BOARD OF COUNTY COMMISSIONERS OF WASHINGTON COUNTY, WASHINGTON, AS FOLLOWS:
                
                Section 1. Special Assessment District Guidelines.
                
                (a) Establishment Criteria:
                    (1) A special assessment district may be established upon petition of property owners representing at least sixty percent of the assessed valuation within the proposed district;
                    (2) The proposed improvements must provide specific benefits to properties within the district;
                    (3) An engineering report must document the necessity, cost, and benefit distribution of proposed improvements; and
                    (4) A public hearing must be held with proper notice to all affected property owners.
                
                (b) Assessment Methodology:
                    (1) Assessments shall be proportional to the benefits received;
                    (2) The County Assessor shall develop a specific benefit assessment formula for each district;
                    (3) Assessment calculations shall be transparent and available for public review; and
                    (4) Annual adjustments shall be limited to actual cost increases.
                
                (c) Administration and Oversight:
                    (1) Each special assessment district shall have an advisory committee of property owners;
                    (2) Annual financial reports shall be published;
                    (3) The County Assessor shall review assessment methodologies every three years; and
                    (4) Special assessment districts shall automatically terminate upon completion of the financed improvements and repayment of any associated debt.
                
                Section 2. The County Assessor's Office is hereby directed to develop detailed procedures implementing this resolution within ninety days.
                
                ADOPTED by the Board of County Commissioners of Washington County, Washington, at a regular meeting thereof, held this 12th day of April, 2025.
                """,
                'source': 'local_docs',
                'url': 'https://www.co.washington.wa.us/resolutions/WA-2025-021.pdf',
                'status': 'Passed',
                'introduced_date': datetime.now() - timedelta(days=20),
                'last_action_date': datetime.now() - timedelta(days=2),
                'impact_summary': 'Establishes guidelines for special assessment districts, including creation criteria and assessment methodologies.',
                'affected_property_classes': 'Residential, Commercial, Industrial, Agricultural, Vacant Land'
            }
        ]
        
        # Add bills to database
        for bill_data in sample_bills:
            bill = LegislativeUpdate(**bill_data)
            db.session.add(bill)
        
        db.session.commit()
        logger.info(f"Added {len(sample_bills)} sample bills to the database")

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Add sample bills
    add_sample_bills()