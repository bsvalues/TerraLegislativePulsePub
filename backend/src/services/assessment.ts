import { prisma } from '../db';
import { Property, PropertyImprovement, PropertyType, ImprovementType } from '@prisma/client';
import { z } from 'zod';

const AssessmentInputSchema = z.object({
  propertyId: z.string(),
  marketValue: z.number().positive(),
  assessmentDate: z.date(),
  assessorId: z.string(),
  notes: z.string().optional(),
  adjustments: z.array(z.object({
    type: z.string(),
    value: z.number(),
    description: z.string()
  })).optional()
});

type AssessmentInput = z.infer<typeof AssessmentInputSchema>;

interface AssessmentResult {
  propertyId: string;
  marketValue: number;
  assessedValue: number;
  taxValue: number;
  assessmentDate: Date;
  assessorId: string;
  adjustments: {
    type: string;
    value: number;
    description: string;
  }[];
  notes?: string;
}

export class AssessmentService {
  private static readonly BASE_ASSESSMENT_RATIO = 0.7; // 70% of market value
  private static readonly IMPROVEMENT_IMPACT_FACTOR = 0.15; // 15% impact on value
  private static readonly MARKET_TREND_FACTOR = 0.05; // 5% market trend adjustment

  private static readonly PROPERTY_TYPE_MULTIPLIERS: Record<PropertyType, number> = {
    RESIDENTIAL: 1.0,
    COMMERCIAL: 1.2,
    INDUSTRIAL: 1.1,
    AGRICULTURAL: 0.8,
    MIXED_USE: 1.15
  };

  private static readonly IMPROVEMENT_TYPE_MULTIPLIERS: Record<ImprovementType, number> = {
    RENOVATION: 1.2,
    ADDITION: 1.3,
    REPAIR: 0.9,
    MAINTENANCE: 0.8,
    DEMOLITION: 0.5
  };

  async calculateAssessment(input: AssessmentInput): Promise<AssessmentResult> {
    const property = await prisma.property.findUnique({
      where: { id: input.propertyId },
      include: {
        improvements: true,
        taxInfo: true,
        history: {
          where: {
            action: 'ASSESSED'
          },
          orderBy: {
            date: 'desc'
          },
          take: 1
        }
      }
    });

    if (!property) {
      throw new Error('Property not found');
    }

    const baseValue = this.calculateBaseValue(property, input.marketValue);
    const improvementValue = this.calculateImprovementValue(property.improvements);
    const marketTrendValue = this.calculateMarketTrendValue(property, input.marketValue);
    const typeMultiplier = AssessmentService.PROPERTY_TYPE_MULTIPLIERS[property.type];

    const assessedValue = baseValue * typeMultiplier + improvementValue + marketTrendValue;
    const taxValue = this.calculateTaxValue(assessedValue, property.taxInfo?.taxRate);

    const result: AssessmentResult = {
      propertyId: input.propertyId,
      marketValue: input.marketValue,
      assessedValue,
      taxValue,
      assessmentDate: input.assessmentDate,
      assessorId: input.assessorId,
      adjustments: input.adjustments || [],
      notes: input.notes
    };

    await this.saveAssessment(result, property);

    return result;
  }

  private calculateBaseValue(property: Property, marketValue: number): number {
    return marketValue * AssessmentService.BASE_ASSESSMENT_RATIO;
  }

  private calculateImprovementValue(improvements: PropertyImprovement[]): number {
    return improvements.reduce((total, improvement) => {
      const multiplier = AssessmentService.IMPROVEMENT_TYPE_MULTIPLIERS[improvement.type];
      const impact = improvement.value * multiplier * AssessmentService.IMPROVEMENT_IMPACT_FACTOR;
      return total + impact;
    }, 0);
  }

  private calculateMarketTrendValue(property: Property, currentMarketValue: number): number {
    const lastAssessment = property.history[0];
    if (!lastAssessment) {
      return 0;
    }

    const changes = lastAssessment.changes as { field: string; oldValue: number; newValue: number }[];
    const lastValue = changes.find(c => c.field === 'value')?.oldValue || 0;
    
    if (lastValue === 0) {
      return 0;
    }

    const trend = (currentMarketValue - lastValue) / lastValue;
    return currentMarketValue * trend * AssessmentService.MARKET_TREND_FACTOR;
  }

  private calculateTaxValue(assessedValue: number, taxRate?: number): number {
    if (!taxRate) {
      return 0;
    }
    return assessedValue * (taxRate / 100);
  }

  private async saveAssessment(result: AssessmentResult, property: Property): Promise<void> {
    await prisma.propertyHistory.create({
      data: {
        propertyId: result.propertyId,
        action: 'ASSESSED',
        description: 'Property assessment completed',
        userId: result.assessorId,
        changes: {
          field: 'value',
          oldValue: property.value,
          newValue: result.assessedValue
        }
      }
    });

    await prisma.property.update({
      where: { id: result.propertyId },
      data: {
        value: result.assessedValue,
        metadata: {
          update: {
            lastAssessed: result.assessmentDate
          }
        }
      }
    });
  }

  async getAssessmentHistory(propertyId: string): Promise<AssessmentResult[]> {
    const history = await prisma.propertyHistory.findMany({
      where: {
        propertyId,
        action: 'ASSESSED'
      },
      orderBy: {
        date: 'desc'
      },
      include: {
        user: true
      }
    });

    return history.map(record => {
      const changes = record.changes as { field: string; oldValue: number; newValue: number }[];
      return {
        propertyId,
        marketValue: changes.find(c => c.field === 'marketValue')?.newValue || 0,
        assessedValue: changes.find(c => c.field === 'value')?.newValue || 0,
        taxValue: changes.find(c => c.field === 'taxValue')?.newValue || 0,
        assessmentDate: record.date,
        assessorId: record.userId,
        adjustments: [],
        notes: record.description
      };
    });
  }

  async validateAssessment(input: AssessmentInput): Promise<{ isValid: boolean; errors: string[] }> {
    const errors: string[] = [];

    // Validate market value against recent sales
    const recentSales = await this.getRecentSales(input.propertyId);
    const averageSalePrice = this.calculateAverageSalePrice(recentSales);
    
    if (input.marketValue > averageSalePrice * 1.2) {
      errors.push('Market value exceeds recent sales average by more than 20%');
    }

    if (input.marketValue < averageSalePrice * 0.8) {
      errors.push('Market value is below recent sales average by more than 20%');
    }

    // Validate assessor permissions
    const assessor = await prisma.user.findUnique({
      where: { id: input.assessorId }
    });

    if (!assessor || assessor.role !== 'ASSESSOR') {
      errors.push('Invalid assessor credentials');
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }

  private async getRecentSales(propertyId: string): Promise<{ salePrice: number; saleDate: Date }[]> {
    // Implementation would query recent sales data
    return [];
  }

  private calculateAverageSalePrice(sales: { salePrice: number; saleDate: Date }[]): number {
    if (sales.length === 0) return 0;
    return sales.reduce((sum, sale) => sum + sale.salePrice, 0) / sales.length;
  }
} 