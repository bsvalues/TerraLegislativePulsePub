import React from 'react';
import { Card, Typography, Tag, Button, Space, Tooltip, Badge } from 'antd';
import { 
  HomeOutlined, 
  DollarOutlined, 
  CalendarOutlined,
  EnvironmentOutlined,
  EditOutlined,
  HistoryOutlined,
  FileTextOutlined
} from '@ant-design/icons';

const { Title, Text } = Typography;

interface PropertyCardProps {
  property: {
    id: string;
    address: string;
    value: number;
    lastAssessment: string;
    status: 'active' | 'pending' | 'review';
    type: string;
    area: number;
    owner: string;
    history: Array<{
      date: string;
      action: string;
      value: number;
    }>;
  };
  onEdit: (id: string) => void;
  onViewHistory: (id: string) => void;
  onViewDocuments: (id: string) => void;
}

const PropertyCard: React.FC<PropertyCardProps> = ({
  property,
  onEdit,
  onViewHistory,
  onViewDocuments
}) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'success';
      case 'pending': return 'warning';
      case 'review': return 'processing';
      default: return 'default';
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(value);
  };

  return (
    <Card
      hoverable
      className="property-card"
      actions={[
        <Tooltip title="Edit Property">
          <Button 
            type="text" 
            icon={<EditOutlined />} 
            onClick={() => onEdit(property.id)}
          />
        </Tooltip>,
        <Tooltip title="View History">
          <Button 
            type="text" 
            icon={<HistoryOutlined />} 
            onClick={() => onViewHistory(property.id)}
          />
        </Tooltip>,
        <Tooltip title="View Documents">
          <Button 
            type="text" 
            icon={<FileTextOutlined />} 
            onClick={() => onViewDocuments(property.id)}
          />
        </Tooltip>
      ]}
    >
      <Space direction="vertical" size="middle" style={{ width: '100%' }}>
        <div className="property-header">
          <Title level={4}>
            <HomeOutlined /> {property.address}
          </Title>
          <Badge 
            status={getStatusColor(property.status)} 
            text={property.status.toUpperCase()} 
          />
        </div>

        <div className="property-details">
          <Space direction="vertical" size="small">
            <Text>
              <DollarOutlined /> Value: {formatCurrency(property.value)}
            </Text>
            <Text>
              <CalendarOutlined /> Last Assessment: {property.lastAssessment}
            </Text>
            <Text>
              <EnvironmentOutlined /> Area: {property.area} sq ft
            </Text>
          </Space>
        </div>

        <div className="property-tags">
          <Tag color="blue">{property.type}</Tag>
          <Tag color="purple">Owner: {property.owner}</Tag>
        </div>

        <div className="property-history-preview">
          <Text type="secondary">Recent Changes:</Text>
          {property.history.slice(0, 2).map((item, index) => (
            <div key={index} className="history-item">
              <Text type="secondary">{item.date}</Text>
              <Text>{item.action}</Text>
              <Text type="secondary">{formatCurrency(item.value)}</Text>
            </div>
          ))}
        </div>
      </Space>
    </Card>
  );
};

export default PropertyCard; 