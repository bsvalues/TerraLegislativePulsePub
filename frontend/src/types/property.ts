export enum PropertyType {
  RESIDENTIAL = 'RESIDENTIAL',
  COMMERCIAL = 'COMMERCIAL',
  INDUSTRIAL = 'INDUSTRIAL',
  AGRICULTURAL = 'AGRICULTURAL',
  MIXED_USE = 'MIXED_USE'
}

export enum PropertyStatus {
  ACTIVE = 'ACTIVE',
  PENDING = 'PENDING',
  SOLD = 'SOLD',
  FORECLOSED = 'FORECLOSED',
  DELINQUENT = 'DELINQUENT'
}

export interface Property {
  id: string;
  address: {
    street: string;
    city: string;
    state: string;
    zipCode: string;
    county: string;
  };
  value: number;
  type: PropertyType;
  status: PropertyStatus;
  owner: {
    name: string;
    contact: {
      email: string;
      phone: string;
    };
  };
  taxInfo?: {
    taxId: string;
    taxRate: number;
    lastPayment: string;
    nextPayment: string;
  };
  improvements?: PropertyImprovement[];
  documents?: PropertyDocument[];
  history?: PropertyHistory[];
  metadata: {
    createdAt: string;
    updatedAt: string;
    lastAssessed: string;
  };
}

export interface PropertyHistory {
  id: string;
  action: HistoryAction;
  description: string;
  date: string;
  user: {
    id: string;
    name: string;
    role: string;
  };
  changes?: {
    field: string;
    oldValue: any;
    newValue: any;
  }[];
}

export enum HistoryAction {
  CREATED = 'CREATED',
  UPDATED = 'UPDATED',
  DELETED = 'DELETED',
  ASSESSED = 'ASSESSED',
  TAX_PAID = 'TAX_PAID',
  IMPROVEMENT_ADDED = 'IMPROVEMENT_ADDED',
  DOCUMENT_ADDED = 'DOCUMENT_ADDED',
  STATUS_CHANGED = 'STATUS_CHANGED'
}

export interface PropertyDocument {
  id: string;
  name: string;
  type: DocumentType;
  category: DocumentCategory;
  url: string;
  size: number;
  uploadDate: string;
  metadata?: {
    description?: string;
    tags?: string[];
    relatedTo?: string[];
  };
}

export enum DocumentType {
  PDF = 'PDF',
  IMAGE = 'IMAGE',
  TEXT = 'TEXT',
  SPREADSHEET = 'SPREADSHEET',
  OTHER = 'OTHER'
}

export enum DocumentCategory {
  TAX = 'TAX',
  LEGAL = 'LEGAL',
  PERMIT = 'PERMIT',
  INSPECTION = 'INSPECTION',
  CONTRACT = 'CONTRACT',
  OTHER = 'OTHER'
}

export interface PropertyImprovement {
  id: string;
  type: ImprovementType;
  description: string;
  value: number;
  status: ImprovementStatus;
  startDate: string;
  completionDate?: string;
  contractor?: string;
  permits?: string[];
  documents?: string[];
}

export enum ImprovementType {
  RENOVATION = 'RENOVATION',
  ADDITION = 'ADDITION',
  REPAIR = 'REPAIR',
  MAINTENANCE = 'MAINTENANCE',
  DEMOLITION = 'DEMOLITION'
}

export enum ImprovementStatus {
  PLANNED = 'PLANNED',
  IN_PROGRESS = 'IN_PROGRESS',
  COMPLETED = 'COMPLETED',
  CANCELLED = 'CANCELLED',
  ON_HOLD = 'ON_HOLD'
}

export interface PropertyFilter {
  type?: PropertyType;
  status?: PropertyStatus;
  minValue?: number;
  maxValue?: number;
  minArea?: number;
  maxArea?: number;
  owner?: string;
  dateRange?: {
    start: string;
    end: string;
  };
}

export interface PropertySort {
  field: keyof Property;
  order: 'ascend' | 'descend';
} 